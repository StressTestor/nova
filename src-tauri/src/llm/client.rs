use futures_util::StreamExt;
use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Emitter};

use crate::llm::personality;
use crate::state::{AppState, NovaState};

const OLLAMA_URL: &str = "http://127.0.0.1:11434";
const DEFAULT_MODEL: &str = "llama3.1:8b";
const MAX_HISTORY: usize = 20;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ChatMessage {
    role: String,
    content: String,
}

#[derive(Debug, Deserialize)]
struct OllamaResponse {
    message: Option<OllamaMessage>,
    done: bool,
}

#[derive(Debug, Deserialize)]
struct OllamaMessage {
    content: String,
}

#[derive(Debug, Serialize, Clone)]
pub struct LlmToken {
    pub token: String,
    pub done: bool,
}

pub struct LlmClient {
    http: reqwest::Client,
    history: Vec<ChatMessage>,
    model: String,
}

impl LlmClient {
    pub fn new() -> Self {
        Self {
            http: reqwest::Client::new(),
            history: vec![],
            model: DEFAULT_MODEL.to_string(),
        }
    }

    pub async fn check_status(&self) -> Result<bool, String> {
        match self.http.get(format!("{}/api/tags", OLLAMA_URL)).send().await {
            Ok(resp) => Ok(resp.status().is_success()),
            Err(_) => Ok(false),
        }
    }

    pub async fn send_message(
        &mut self,
        text: &str,
        app: &AppHandle,
        app_state: &AppState,
    ) -> Result<String, String> {
        self.history.push(ChatMessage {
            role: "user".to_string(),
            content: text.to_string(),
        });

        while self.history.len() > MAX_HISTORY {
            self.history.remove(0);
        }

        let mut messages = vec![ChatMessage {
            role: "system".to_string(),
            content: personality::get_system_prompt().to_string(),
        }];
        messages.extend(self.history.clone());

        let (abort_tx, mut abort_rx) = tokio::sync::oneshot::channel::<()>();
        app_state.set_abort_handle(abort_tx);
        app_state.set_state(app, NovaState::Thinking);

        let body = serde_json::json!({
            "model": self.model,
            "messages": messages,
            "stream": true,
        });

        let response = match self.http
            .post(format!("{}/api/chat", OLLAMA_URL))
            .json(&body)
            .send()
            .await
        {
            Ok(r) => r,
            Err(e) => {
                app_state.set_state(app, NovaState::Idle);
                return Err(format!("Ollama connection failed: {}", e));
            }
        };

        if !response.status().is_success() {
            app_state.set_state(app, NovaState::Idle);
            return Err(format!("Ollama error: {}", response.status()));
        }

        let mut stream = response.bytes_stream();
        let mut full_response = String::new();
        let mut first_token = true;

        loop {
            tokio::select! {
                _ = &mut abort_rx => {
                    tracing::info!("LLM stream aborted");
                    let _ = app.emit("llm_interrupted", ());
                    app_state.set_state(app, NovaState::Idle);
                    if !full_response.is_empty() {
                        self.history.push(ChatMessage {
                            role: "assistant".to_string(),
                            content: full_response.clone(),
                        });
                    }
                    return Ok(full_response);
                }
                chunk = stream.next() => {
                    match chunk {
                        Some(Ok(bytes)) => {
                            let text = String::from_utf8_lossy(&bytes);
                            for line in text.lines() {
                                if line.trim().is_empty() {
                                    continue;
                                }
                                match serde_json::from_str::<OllamaResponse>(line) {
                                    Ok(resp) => {
                                        if let Some(msg) = resp.message {
                                            if first_token {
                                                app_state.set_state(app, NovaState::Speaking);
                                                first_token = false;
                                            }
                                            full_response.push_str(&msg.content);
                                            let _ = app.emit("llm_token", LlmToken {
                                                token: msg.content,
                                                done: false,
                                            });
                                        }
                                        if resp.done {
                                            let _ = app.emit("llm_token", LlmToken {
                                                token: String::new(),
                                                done: true,
                                            });
                                        }
                                    }
                                    Err(e) => {
                                        tracing::warn!("Failed to parse Ollama line: {}", e);
                                    }
                                }
                            }
                        }
                        Some(Err(e)) => {
                            tracing::error!("Stream error: {}", e);
                            break;
                        }
                        None => break,
                    }
                }
            }
        }

        if !full_response.is_empty() {
            self.history.push(ChatMessage {
                role: "assistant".to_string(),
                content: full_response.clone(),
            });
        }

        app_state.set_state(app, NovaState::Idle);
        Ok(full_response)
    }
}
