use std::process::Command;

pub fn execute(script: &str) -> Result<String, String> {
    let output = Command::new("osascript")
        .arg("-e")
        .arg(script)
        .output()
        .map_err(|e| format!("Failed to run osascript: {}", e))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("AppleScript error: {}", stderr.trim()))
    }
}

pub fn set_volume(level: u8) -> Result<String, String> {
    let clamped = level.min(100);
    let script = format!("set volume output volume {}", clamped);
    execute(&script)?;
    Ok(format!("Volume set to {}%.", clamped))
}

pub fn get_clipboard() -> Result<String, String> {
    execute("the clipboard")
}
