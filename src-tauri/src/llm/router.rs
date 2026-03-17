use regex::Regex;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SystemAction {
    OpenApp { name: String },
    SetVolume { level: u8 },
    GetBattery,
    GetSystemInfo,
    GetClipboard,
    Goodnight,
}

#[derive(Debug)]
pub enum RouterResult {
    System(SystemAction),
    Llm,
}

fn validate_app_name(name: &str) -> Option<String> {
    let trimmed = name.trim();
    if trimmed.is_empty() || trimmed.len() > 100 {
        return None;
    }
    let re = Regex::new(r"^[a-zA-Z0-9 .\-]+$").unwrap();
    if re.is_match(trimmed) {
        Some(trimmed.to_string())
    } else {
        None
    }
}

fn validate_volume(s: &str) -> Option<u8> {
    s.trim().parse::<u8>().ok().filter(|&v| v <= 100)
}

pub fn classify(input: &str) -> RouterResult {
    let input = input.trim();
    if input.is_empty() {
        return RouterResult::Llm;
    }

    // Open/launch app
    let re_open = Regex::new(r"(?i)^(?:open|launch|start)\s+(.+)$").unwrap();
    if let Some(caps) = re_open.captures(input) {
        if let Some(name) = validate_app_name(&caps[1]) {
            return RouterResult::System(SystemAction::OpenApp { name });
        }
    }

    // Set volume
    let re_vol = Regex::new(r"(?i)^set\s+(?:the\s+)?volume\s+(?:to\s+)?(\d+)").unwrap();
    if let Some(caps) = re_vol.captures(input) {
        if let Some(level) = validate_volume(&caps[1]) {
            return RouterResult::System(SystemAction::SetVolume { level });
        }
    }

    // Battery
    let re_bat = Regex::new(r"(?i)(?:what(?:'s|s| is)\s+(?:my\s+)?battery|battery\s+(?:level|status|percentage))").unwrap();
    if re_bat.is_match(input) {
        return RouterResult::System(SystemAction::GetBattery);
    }

    // System info
    let re_sys = Regex::new(r"(?i)(?:system\s+(?:info|status|health)|what(?:'s|s| is)\s+(?:my\s+)?(?:system|computer|mac)\s+(?:status|info))").unwrap();
    if re_sys.is_match(input) {
        return RouterResult::System(SystemAction::GetSystemInfo);
    }

    // Clipboard
    let re_clip = Regex::new(r"(?i)(?:what(?:'s|s| is)\s+(?:in\s+(?:my\s+)?)?clipboard|paste(?:board)?|clipboard)").unwrap();
    if re_clip.is_match(input) {
        return RouterResult::System(SystemAction::GetClipboard);
    }

    // Goodnight
    let re_gn = Regex::new(r"(?i)^(?:good\s*night|power\s+down|shut\s*down|go\s+to\s+sleep|sleep)$").unwrap();
    if re_gn.is_match(input) {
        return RouterResult::System(SystemAction::Goodnight);
    }

    RouterResult::Llm
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_open_app() {
        match classify("open Finder") {
            RouterResult::System(SystemAction::OpenApp { name }) => assert_eq!(name, "Finder"),
            _ => panic!("Expected OpenApp"),
        }
    }

    #[test]
    fn test_open_multiword() {
        match classify("open Google Chrome") {
            RouterResult::System(SystemAction::OpenApp { name }) => assert_eq!(name, "Google Chrome"),
            _ => panic!("Expected OpenApp"),
        }
    }

    #[test]
    fn test_launch_variant() {
        match classify("launch Safari") {
            RouterResult::System(SystemAction::OpenApp { name }) => assert_eq!(name, "Safari"),
            _ => panic!("Expected OpenApp"),
        }
    }

    #[test]
    fn test_rejects_shell_injection() {
        assert!(matches!(classify("open $(rm -rf ~)"), RouterResult::Llm));
    }

    #[test]
    fn test_rejects_semicolon() {
        assert!(matches!(classify("open Finder; do shell script \"bad\""), RouterResult::Llm));
    }

    #[test]
    fn test_rejects_backticks() {
        assert!(matches!(classify("open `whoami`"), RouterResult::Llm));
    }

    #[test]
    fn test_rejects_empty_app() {
        assert!(matches!(classify("open "), RouterResult::Llm));
    }

    #[test]
    fn test_set_volume() {
        match classify("set volume to 50") {
            RouterResult::System(SystemAction::SetVolume { level }) => assert_eq!(level, 50),
            _ => panic!("Expected SetVolume"),
        }
    }

    #[test]
    fn test_volume_over_100() {
        assert!(matches!(classify("set volume to 150"), RouterResult::Llm));
    }

    #[test]
    fn test_battery() {
        assert!(matches!(classify("what's my battery"), RouterResult::System(SystemAction::GetBattery)));
    }

    #[test]
    fn test_battery_variant() {
        assert!(matches!(classify("battery level"), RouterResult::System(SystemAction::GetBattery)));
    }

    #[test]
    fn test_goodnight() {
        assert!(matches!(classify("goodnight"), RouterResult::System(SystemAction::Goodnight)));
    }

    #[test]
    fn test_fallthrough() {
        assert!(matches!(classify("what is the meaning of life?"), RouterResult::Llm));
    }

    #[test]
    fn test_case_insensitive() {
        assert!(matches!(classify("OPEN FINDER"), RouterResult::System(SystemAction::OpenApp { .. })));
    }

    #[test]
    fn test_empty() {
        assert!(matches!(classify(""), RouterResult::Llm));
    }

    #[test]
    fn test_whitespace() {
        assert!(matches!(classify("   "), RouterResult::Llm));
    }
}
