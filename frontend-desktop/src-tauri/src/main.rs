// Tauri main.rs - Desktop app entry point
#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::{
    SystemTray, SystemTrayMenu, SystemTrayMenuItem, Menu, MenuItem, Submenu,
    CustomMenuItem, Manager, WindowEvent,
};

fn main() {
    let sys_tray_menu = SystemTrayMenu::new()
        .add_item(CustomMenuItem::new("show", "Show"))
        .add_item(CustomMenuItem::new("chat", "Open Chat"))
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(CustomMenuItem::new("quit", "Quit"));

    let sys_tray = SystemTray::new()
        .with_menu(sys_tray_menu)
        .with_tooltip("Buddy AI OS");

    let menu = Menu::new()
        .add_submenu(Submenu::new(
            "File",
            Menu::new()
                .add_item(MenuItem::Quit),
        ))
        .add_submenu(Submenu::new(
            "Edit",
            Menu::new()
                .add_item(MenuItem::Copy)
                .add_item(MenuItem::Paste),
        ))
        .add_submenu(Submenu::new(
            "View",
            Menu::new()
                .add_item(MenuItem::Reload)
                .add_item(MenuItem::InspectElement),
        ));

    tauri::Builder::default()
        .menu(menu)
        .system_tray(sys_tray)
        .on_system_tray_event(|app, event| match event {
            tauri::SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                "chat" => {
                    if let Ok(window) = app.get_window("chat") {
                        window.show().unwrap();
                        window.set_focus().unwrap();
                    }
                }
                "quit" => {
                    std::process::exit(0);
                }
                _ => {}
            },
            tauri::SystemTrayEvent::LeftClick { .. } => {
                let window = app.get_window("main").unwrap();
                if window.is_visible().unwrap() {
                    window.hide().unwrap();
                } else {
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
            }
            _ => {}
        })
        .on_window_event(|event| match event.event() {
            WindowEvent::CloseRequested { api, .. } => {
                #[cfg(target_os = "macos")]
                {
                    api.prevent_close();
                    event.window().hide().unwrap();
                }
                #[cfg(not(target_os = "macos"))]
                {}
            }
            _ => {}
        })
        .invoke_handler(tauri::generate_handler![
            cmd::process_intent,
            cmd::get_agents,
            cmd::save_memory,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

mod cmd {
    use serde::{Deserialize, Serialize};

    #[derive(Serialize, Deserialize, Debug)]
    pub struct IntentRequest {
        pub user_id: String,
        pub intent: String,
        pub context: serde_json::Value,
    }

    #[tauri::command]
    pub async fn process_intent(request: IntentRequest) -> Result<serde_json::Value, String> {
        // Send to Buddy Core API
        let client = reqwest::Client::new();
        let response = client
            .post("http://localhost:8000/api/v1/intents/process")
            .json(&request)
            .send()
            .await
            .map_err(|e| e.to_string())?;

        let data = response.json().await.map_err(|e| e.to_string())?;
        Ok(data)
    }

    #[tauri::command]
    pub async fn get_agents() -> Result<Vec<serde_json::Value>, String> {
        let client = reqwest::Client::new();
        let response = client
            .get("http://localhost:8000/api/v1/agents")
            .send()
            .await
            .map_err(|e| e.to_string())?;

        let data: Vec<serde_json::Value> = response.json().await.map_err(|e| e.to_string())?;
        Ok(data)
    }

    #[tauri::command]
    pub async fn save_memory(
        user_id: String,
        memory_type: String,
        content: String,
    ) -> Result<String, String> {
        let client = reqwest::Client::new();
        let response = client
            .post("http://localhost:8000/api/v1/memory/save")
            .json(&serde_json::json!({
                "user_id": user_id,
                "memory_type": memory_type,
                "content": content,
            }))
            .send()
            .await
            .map_err(|e| e.to_string())?;

        let data: serde_json::Value = response.json().await.map_err(|e| e.to_string())?;
        Ok(data.to_string())
    }
}
