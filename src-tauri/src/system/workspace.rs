use std::process::Command;

pub fn open_app(name: &str) -> Result<String, String> {
    let output = Command::new("open")
        .arg("-a")
        .arg(name)
        .output()
        .map_err(|e| format!("Failed to open app: {}", e))?;

    if output.status.success() {
        Ok(format!("Opened {}.", name))
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        if stderr.contains("Unable to find application") {
            Err(format!("{} not found.", name))
        } else {
            Err(format!("Failed to open {}: {}", name, stderr.trim()))
        }
    }
}
