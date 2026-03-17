mod llm;
mod state;
mod system;
mod voice;

use tauri::{Emitter, Manager};
use tauri_plugin_global_shortcut::{GlobalShortcutExt, ShortcutState};
use tokio::sync::Mutex;

use llm::client::LlmClient;
use llm::router::{self, RouterResult, SystemAction};
use state::{AppState, NovaState};

#[tauri::command]
async fn send_message(
    text: String,
    app: tauri::AppHandle,
    app_state: tauri::State<'_, AppState>,
    llm: tauri::State<'_, Mutex<LlmClient>>,
) -> Result<String, String> {
    let text = text.trim().to_string();
    if text.is_empty() {
        return Ok(String::new());
    }

    app_state.cancel_stream();

    match router::classify(&text) {
        RouterResult::System(action) => {
            app_state.set_state(&app, NovaState::Thinking);

            let result = match action {
                SystemAction::OpenApp { name } => system::workspace::open_app(&name),
                SystemAction::SetVolume { level } => system::applescript::set_volume(level),
                SystemAction::GetBattery => system::info::get_battery(),
                SystemAction::GetSystemInfo => {
                    system::info::get_system_info()
                        .map(|info| system::info::format_system_info(&info))
                }
                SystemAction::GetClipboard => system::applescript::get_clipboard(),
                SystemAction::Goodnight => {
                    app_state.set_state(&app, NovaState::PoweringDown);
                    Ok("Goodnight.".to_string())
                }
            };

            match &result {
                Ok(msg) => {
                    app_state.set_state(&app, NovaState::Speaking);
                    voice::tts::speak(msg, &app);
                    let app_c = app.clone();
                    let state_c = app_state.inner().clone();
                    tokio::spawn(async move {
                        tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;
                        if state_c.get_state() == NovaState::Speaking {
                            state_c.set_state(&app_c, NovaState::Idle);
                        }
                    });
                }
                Err(_) => {
                    app_state.set_state(&app, NovaState::Idle);
                }
            }

            result
        }
        RouterResult::Llm => {
            let mut client = llm.lock().await;
            let response = client.send_message(&text, &app, &app_state).await?;

            if !response.is_empty() {
                voice::tts::speak(&response, &app);
            }

            Ok(response)
        }
    }
}

#[tauri::command]
async fn get_llm_status(llm: tauri::State<'_, Mutex<LlmClient>>) -> Result<bool, String> {
    let client = llm.lock().await;
    client.check_status().await
}

pub fn run() {
    tracing_subscriber::fmt()
        .with_env_filter("nova=debug")
        .init();

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .manage(AppState::new())
        .manage(Mutex::new(LlmClient::new()))
        .invoke_handler(tauri::generate_handler![send_message, get_llm_status])
        .setup(|app| {
            tracing::info!("NOVA initializing");

            // Global shortcut: Cmd+Shift+N
            app.global_shortcut().on_shortcut(
                "CmdOrCtrl+Shift+N",
                move |_app, _shortcut, event| {
                    if event.state == ShortcutState::Pressed {
                        if let Some(win) = _app.get_webview_window("main") {
                            if win.is_visible().unwrap_or(false) {
                                let _ = win.hide();
                            } else {
                                let _ = win.show();
                                let _ = win.set_focus();
                            }
                        }
                    }
                },
            )?;

            // System tray
            use tauri::tray::TrayIconBuilder;
            let _tray = TrayIconBuilder::new()
                .tooltip("NOVA")
                .on_tray_icon_event(move |tray, event| {
                    if let tauri::tray::TrayIconEvent::Click { .. } = event {
                        if let Some(win) = tray.app_handle().get_webview_window("main") {
                            if win.is_visible().unwrap_or(false) {
                                let _ = win.hide();
                            } else {
                                let _ = win.show();
                                let _ = win.set_focus();
                            }
                        }
                    }
                })
                .build(app)?;

            // Check Ollama on startup
            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                let client = LlmClient::new();
                match client.check_status().await {
                    Ok(true) => {
                        tracing::info!("Ollama connected");
                        let _ = handle.emit("ollama_status", "online");
                    }
                    _ => {
                        tracing::warn!("Ollama not available");
                        let _ = handle.emit("ollama_status", "offline");
                    }
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running NOVA");
}
