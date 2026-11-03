use jeb_core::Traffic;
use serde_json::Value;
use tauri::{Emitter, Manager, PhysicalPosition, State};

#[tauri::command]
async fn global_flights(t: State<'_, Traffic>) -> Result<Value, String> {
    let f = t.global().await.ok_or("flight feed unavailable")?;
    serde_json::to_value(f).map_err(|e| e.to_string())
}

#[tauri::command]
async fn near_flights(t: State<'_, Traffic>, lat: f64, lon: f64) -> Result<Value, String> {
    let f = t.near(lat, lon).await.ok_or("nearby feed unavailable")?;
    serde_json::to_value(f).map_err(|e| e.to_string())
}

#[tauri::command]
async fn photo(t: State<'_, Traffic>, reg: String) -> Result<Value, String> {
    Ok(t.photo(&reg).await.unwrap_or(Value::Null))
}

#[tauri::command]
async fn route(t: State<'_, Traffic>, call: String) -> Result<Value, String> {
    Ok(t.route(&call).await.unwrap_or(Value::Null))
}

/// The notch is a separate borderless always-on-top window pinned to the top-centre of the screen.
fn show_notch(app: &tauri::AppHandle) {
    if let Some(w) = app.get_webview_window("notch") {
        if let Ok(Some(m)) = w.current_monitor().or_else(|_| w.primary_monitor()) {
            let width = (320.0 * w.scale_factor().unwrap_or(1.0)) as i32;   // fixed notch window width from tauri.conf.json
            let x = m.position().x + (m.size().width as i32 - width) / 2;
            let _ = w.set_position(PhysicalPosition::new(x, m.position().y));
        }
        let _ = w.show();
    }
}

#[tauri::command]
async fn geocode(t: State<'_, Traffic>, q: String) -> Result<Value, String> {
    Ok(t.geocode(&q).await.unwrap_or(Value::Null))
}

#[tauri::command]
fn hide_notch(app: tauri::AppHandle) {
    if let Some(w) = app.get_webview_window("notch") { let _ = w.hide(); }
}

/// Relay the voice daemon's event stream (state, user, jeb, model) to every window.
async fn relay_daemon_events(app: tauri::AppHandle) {
    let client = reqwest::Client::new();
    loop {
        if let Ok(mut resp) = client.get("http://127.0.0.1:7777/events").send().await {
            let mut buf = String::new();
            while let Ok(Some(chunk)) = resp.chunk().await {
                buf.push_str(&String::from_utf8_lossy(&chunk));
                while let Some(i) = buf.find("\n\n") {
                    let block: String = buf.drain(..i + 2).collect();
                    if let Some(json) = block.strip_prefix("data: ") {
                        if let Ok(v) = serde_json::from_str::<Value>(json.trim()) {
                            if v["kind"] == "map" {
                                if let Some(w) = app.get_webview_window("main") {
                                    if v["action"] == "hide" { let _ = w.hide(); } else { let _ = w.show(); let _ = w.unminimize(); let _ = w.set_focus(); }
                                }
                            }
                            if v["kind"] == "state" && v["state"] != "idle" { show_notch(&app); }
                            if v["kind"] == "user" || v["kind"] == "jeb" { show_notch(&app); }
                            let _ = app.emit("jeb-event", v);
                        }
                    }
                }
            }
        }
        tokio::time::sleep(std::time::Duration::from_secs(2)).await;
    }
}

fn main() {
    // Wayland compositors refuse client-chosen window positions, so run through XWayland to pin the notch at the top.
    if std::env::var_os("GDK_BACKEND").is_none() { std::env::set_var("GDK_BACKEND", "x11"); }
    std::env::set_var("WEBKIT_DISABLE_DMABUF_RENDERER", "1");
    tauri::Builder::default()
        .manage(Traffic::from_env())
        .on_window_event(|w, ev| {   // closing the map only hides it; Jeb keeps running for the notch
            if let tauri::WindowEvent::CloseRequested { api, .. } = ev { if w.label() == "main" { api.prevent_close(); let _ = w.hide(); } }
        })
        .setup(|app| {
            // A dock-type window may sit over the GNOME top bar instead of below it, like a hardware notch.
            if let Some(w) = app.get_webview_window("notch") {
                if let Ok(g) = w.gtk_window() { use gtk::prelude::GtkWindowExt; g.set_type_hint(gtk::gdk::WindowTypeHint::Dock); }
            }
            tauri::async_runtime::spawn(relay_daemon_events(app.handle().clone())); Ok(())
        })
        .invoke_handler(tauri::generate_handler![global_flights, near_flights, photo, route, geocode, hide_notch])
        .run(tauri::generate_context!())
        .expect("failed to run Jeb");
}
