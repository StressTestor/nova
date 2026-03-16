use tauri::Manager;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("NOVA online. Hello, {}.", name)
}

pub fn run() {
    let _ = tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::new("nova=debug"))
        .try_init();

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .invoke_handler(tauri::generate_handler![greet])
        .setup(|app| {
            let window = app.get_webview_window("main").unwrap();
            tracing::info!("NOVA window initialized: {:?}", window.label());
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running NOVA");
}
