use serde::Serialize;
use sysinfo::System;
use std::process::Command;

#[derive(Debug, Serialize)]
pub struct SystemInfo {
    pub memory_used_gb: f64,
    pub memory_total_gb: f64,
    pub disk_used_gb: f64,
    pub disk_total_gb: f64,
    pub uptime_hours: f64,
}

pub fn get_battery() -> Result<String, String> {
    let output = Command::new("pmset")
        .arg("-g")
        .arg("batt")
        .output()
        .map_err(|e| format!("Failed to check battery: {}", e))?;

    let text = String::from_utf8_lossy(&output.stdout);

    if let Some(pct_str) = text.split('\t').nth(1) {
        if let Some(pct) = pct_str.split(';').next() {
            return Ok(format!("Battery at {}.", pct.trim()));
        }
    }

    if text.contains("No battery") || text.contains("Now drawing from 'AC Power'") {
        return Ok("No battery. Running on AC power.".to_string());
    }

    Ok(format!("Battery status: {}", text.trim()))
}

pub fn get_system_info() -> Result<SystemInfo, String> {
    let mut sys = System::new_all();
    sys.refresh_all();

    let memory_total = sys.total_memory() as f64 / 1_073_741_824.0;
    let memory_used = sys.used_memory() as f64 / 1_073_741_824.0;

    let disks = sysinfo::Disks::new_with_refreshed_list();
    let (disk_total, disk_used) = disks
        .iter()
        .find(|d| d.mount_point() == std::path::Path::new("/"))
        .map(|d| {
            let total = d.total_space() as f64 / 1_073_741_824.0;
            let available = d.available_space() as f64 / 1_073_741_824.0;
            (total, total - available)
        })
        .unwrap_or((0.0, 0.0));

    let uptime = System::uptime() as f64 / 3600.0;

    Ok(SystemInfo {
        memory_used_gb: (memory_used * 10.0).round() / 10.0,
        memory_total_gb: (memory_total * 10.0).round() / 10.0,
        disk_used_gb: (disk_used * 10.0).round() / 10.0,
        disk_total_gb: (disk_total * 10.0).round() / 10.0,
        uptime_hours: (uptime * 10.0).round() / 10.0,
    })
}

pub fn format_system_info(info: &SystemInfo) -> String {
    format!(
        "Memory: {:.1}/{:.1} GB. Disk: {:.1}/{:.1} GB. Uptime: {:.1} hours.",
        info.memory_used_gb, info.memory_total_gb,
        info.disk_used_gb, info.disk_total_gb,
        info.uptime_hours
    )
}
