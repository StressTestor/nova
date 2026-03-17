use std::process::Command;
use tauri::{AppHandle, Emitter};

pub fn speak(text: &str, app: &AppHandle) {
    if text.trim().is_empty() {
        return;
    }

    let word_count = text.split_whitespace().count();
    let duration_ms = (word_count as f64 / 4.0 * 1000.0) as u64;

    let app_clone = app.clone();
    let text_owned = text.to_string();

    std::thread::spawn(move || {
        let child = Command::new("say")
            .arg("-r")
            .arg("180")
            .arg(&text_owned)
            .spawn();

        match child {
            Ok(mut proc) => {
                emit_phoneme_animation(&app_clone, &text_owned, duration_ms);
                let _ = proc.wait();
                let _ = app_clone.emit("tts_done", ());
            }
            Err(e) => {
                tracing::error!("TTS failed: {}", e);
                let _ = app_clone.emit("tts_done", ());
            }
        }
    });
}

fn emit_phoneme_animation(app: &AppHandle, text: &str, duration_ms: u64) {
    let chars: Vec<char> = text.chars().collect();
    if chars.is_empty() {
        return;
    }

    let ms_per_char = duration_ms as f64 / chars.len() as f64;
    let step_ms: u64 = 50;
    let mut time: u64 = 0;

    while time < duration_ms {
        let char_idx = ((time as f64 / ms_per_char) as usize).min(chars.len() - 1);
        let c = chars[char_idx];

        let amplitude: f32 = if c.is_whitespace() {
            0.0
        } else if "aeiouAEIOU".contains(c) {
            0.7 + 0.3 * (time as f64 * 0.01).sin().abs() as f32
        } else {
            0.3 + 0.2 * (time as f64 * 0.015).sin().abs() as f32
        };

        let _ = app.emit("jaw_amplitude", amplitude);
        std::thread::sleep(std::time::Duration::from_millis(step_ms));
        time += step_ms;
    }

    let _ = app.emit("jaw_amplitude", 0.0f32);
}
