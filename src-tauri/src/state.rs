use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use tauri::{AppHandle, Emitter};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum NovaState {
    Materializing,
    Idle,
    Thinking,
    Speaking,
    Glitch,
    PoweringDown,
    Sleeping,
}

#[derive(Clone)]
pub struct AppState {
    pub current_state: Arc<Mutex<NovaState>>,
    pub abort_handle: Arc<Mutex<Option<tokio::sync::oneshot::Sender<()>>>>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            current_state: Arc::new(Mutex::new(NovaState::Idle)),
            abort_handle: Arc::new(Mutex::new(None)),
        }
    }

    pub fn set_state(&self, app: &AppHandle, new_state: NovaState) {
        let mut state = self.current_state.lock().unwrap();
        if *state == new_state {
            return;
        }
        tracing::info!("State: {:?} -> {:?}", *state, new_state);
        *state = new_state.clone();
        let _ = app.emit("state_change", new_state);
    }

    pub fn get_state(&self) -> NovaState {
        self.current_state.lock().unwrap().clone()
    }

    pub fn cancel_stream(&self) {
        let mut handle = self.abort_handle.lock().unwrap();
        if let Some(sender) = handle.take() {
            let _ = sender.send(());
        }
    }

    pub fn set_abort_handle(&self, sender: tokio::sync::oneshot::Sender<()>) {
        let mut handle = self.abort_handle.lock().unwrap();
        if let Some(old) = handle.take() {
            let _ = old.send(());
        }
        *handle = Some(sender);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_state_default_idle() {
        let state = AppState::new();
        assert_eq!(state.get_state(), NovaState::Idle);
    }

    #[test]
    fn test_state_can_change() {
        let state = AppState::new();
        {
            let mut s = state.current_state.lock().unwrap();
            *s = NovaState::Thinking;
        }
        assert_eq!(state.get_state(), NovaState::Thinking);
    }

    #[test]
    fn test_cancel_stream_no_panic_when_empty() {
        let state = AppState::new();
        state.cancel_stream(); // should not panic
    }
}
