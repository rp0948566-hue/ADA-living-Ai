//! Live air-traffic data for Jeb. Every value comes from a real public feed; when a feed fails the last
//! good copy is served and flagged stale, never invented.
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{collections::HashMap, sync::Arc, time::{Duration, Instant}};
use tokio::sync::Mutex;

const UA: &str = "JebAI/1.0 (personal local assistant, not public)";

/// One aircraft in SI units: metres, m/s, degrees.
#[derive(Clone, Debug, Serialize, Deserialize, Default)]
pub struct Aircraft {
    pub hex: String,
    pub call: String,
    pub lat: f64,
    pub lon: f64,
    pub alt: f64,
    pub vel: f64,
    pub hdg: f64,
    pub vr: f64,
    pub kind: Option<String>,
    pub reg: Option<String>,
    pub squawk: Option<String>,
    pub mach: Option<f64>,
}

#[derive(Serialize)]
pub struct Feed {
    pub aircraft: Vec<Aircraft>,
    pub source: &'static str,
    pub age_s: u64,
    pub stale: bool,
}

struct Slot<T> { at: Instant, val: T }

#[derive(Clone)]
pub struct Traffic {
    http: reqwest::Client,
    opensky_id: Option<String>,
    opensky_secret: Option<String>,
    token: Arc<Mutex<Option<(Instant, String)>>>,
    global: Arc<Mutex<Option<Slot<Vec<Aircraft>>>>>,
    near: Arc<Mutex<HashMap<(i32, i32), Slot<Vec<Aircraft>>>>>,
    photos: Arc<Mutex<HashMap<String, Value>>>,
    routes: Arc<Mutex<HashMap<String, Value>>>,
}

impl Traffic {
    /// Keys are optional: OPENSKY_CLIENT_ID / OPENSKY_CLIENT_SECRET raise the global rate limit.
    pub fn from_env() -> Self {
        Self {
            http: reqwest::Client::builder().user_agent(UA).timeout(Duration::from_secs(30)).build().expect("http client"),
            opensky_id: std::env::var("OPENSKY_CLIENT_ID").ok().filter(|s| !s.is_empty()),
            opensky_secret: std::env::var("OPENSKY_CLIENT_SECRET").ok().filter(|s| !s.is_empty()),
            token: Default::default(), global: Default::default(), near: Default::default(), photos: Default::default(), routes: Default::default(),
        }
    }

    async fn bearer(&self) -> Option<String> {
        let (id, secret) = (self.opensky_id.as_ref()?, self.opensky_secret.as_ref()?);
        let mut t = self.token.lock().await;
        if let Some((exp, tok)) = t.as_ref() { if *exp > Instant::now() { return Some(tok.clone()); } }
        let r: Value = self.http.post("https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token")
            .form(&[("grant_type", "client_credentials"), ("client_id", id.as_str()), ("client_secret", secret.as_str())])
            .send().await.ok()?.json().await.ok()?;
        let tok = r["access_token"].as_str()?.to_string();
        *t = Some((Instant::now() + Duration::from_secs(r["expires_in"].as_u64().unwrap_or(1800).saturating_sub(60)), tok.clone()));
        Some(tok)
    }

    /// Worldwide airborne traffic. Anonymous OpenSky allows ~100 pulls/day, so refresh at most every 15 min
    /// (every 10 s with credentials); the UI dead-reckons positions in between.
    pub async fn global(&self) -> Option<Feed> {
        let ttl = if self.opensky_id.is_some() { 10 } else { 900 };
        let mut g = self.global.lock().await;
        if let Some(s) = g.as_ref() { if s.at.elapsed().as_secs() < ttl { return Some(feed(&s.val, "opensky", s.at, false)); } }
        let mut req = self.http.get("https://opensky-network.org/api/states/all");
        if let Some(b) = self.bearer().await { req = req.bearer_auth(b); }
        let fresh = async { req.send().await.ok()?.error_for_status().ok()?.json::<Value>().await.ok() }.await;
        match fresh.and_then(|v| parse_opensky(&v)) {
            Some(list) => { let f = feed(&list, "opensky", Instant::now(), false); *g = Some(Slot { at: Instant::now(), val: list }); Some(f) }
            None => g.as_ref().map(|s| feed(&s.val, "opensky", s.at, true)),
        }
    }

    /// Rich detail (type, registration, squawk, Mach) within 250 nm of a point, from adsb.lol, cached 5 s.
    pub async fn near(&self, lat: f64, lon: f64) -> Option<Feed> {
        let key = ((lat * 10.0).round() as i32, (lon * 10.0).round() as i32);
        let mut n = self.near.lock().await;
        if let Some(s) = n.get(&key) { if s.at.elapsed().as_secs() < 5 { return Some(feed(&s.val, "adsb.lol", s.at, false)); } }
        let url = format!("https://api.adsb.lol/v2/point/{lat:.4}/{lon:.4}/250");
        let fresh = async { self.http.get(url).send().await.ok()?.error_for_status().ok()?.json::<Value>().await.ok() }.await;
        match fresh.and_then(|v| parse_adsb(&v)) {
            Some(list) => { let f = feed(&list, "adsb.lol", Instant::now(), false); n.insert(key, Slot { at: Instant::now(), val: list }); Some(f) }
            None => n.get(&key).map(|s| feed(&s.val, "adsb.lol", s.at, true)),
        }
    }

    pub async fn photo(&self, reg: &str) -> Option<Value> {
        if let Some(p) = self.photos.lock().await.get(reg) { return Some(p.clone()); }
        let v: Value = self.http.get(format!("https://api.planespotters.net/pub/photos/reg/{reg}")).send().await.ok()?.json().await.ok()?;
        let p = v["photos"].get(0)?;
        let out = serde_json::json!({ "src": p["thumbnail_large"]["src"], "by": p["photographer"] });
        self.photos.lock().await.insert(reg.to_string(), out.clone());
        Some(out)
    }
}

impl Traffic {
    /// Place name to coordinates via OpenStreetMap Nominatim (one request per spoken place, cached by the server's own rules).
    pub async fn geocode(&self, q: &str) -> Option<Value> {
        let v: Value = self.http.get("https://nominatim.openstreetmap.org/search").query(&[("q", q), ("format", "json"), ("limit", "1")])
            .send().await.ok()?.error_for_status().ok()?.json().await.ok()?;
        let p = v.get(0)?;
        Some(serde_json::json!({ "lat": p["lat"].as_str()?.parse::<f64>().ok()?, "lon": p["lon"].as_str()?.parse::<f64>().ok()?, "name": p["display_name"] }))
    }

    /// Scheduled origin/destination for a callsign (community standing data, so a schedule, not a live filing).
    pub async fn route(&self, call: &str) -> Option<Value> {
        let call = call.trim().to_uppercase();
        if call.len() < 3 || !call.chars().all(|c| c.is_ascii_alphanumeric()) { return None; }
        if let Some(r) = self.routes.lock().await.get(&call) { return Some(r.clone()); }
        let url = format!("https://vrs-standing-data.adsb.lol/routes/{}/{}.json", &call[..2], call);
        let v: Value = self.http.get(url).send().await.ok()?.error_for_status().ok()?.json().await.ok()?;
        let a = v["_airports"].as_array()?;
        if a.len() < 2 { return None; }
        let out = serde_json::json!({ "from": a[0], "to": a[a.len() - 1], "scheduled": true });
        self.routes.lock().await.insert(call, out.clone());
        Some(out)
    }
}

fn feed(list: &[Aircraft], source: &'static str, at: Instant, stale: bool) -> Feed {
    Feed { aircraft: list.to_vec(), source, age_s: at.elapsed().as_secs(), stale }
}

pub fn parse_opensky(v: &Value) -> Option<Vec<Aircraft>> {
    let states = v["states"].as_array()?;
    let out: Vec<Aircraft> = states.iter().filter_map(|s| {
        if s[8].as_bool().unwrap_or(false) { return None; }          // on the ground
        Some(Aircraft {
            hex: s[0].as_str()?.to_string(), call: s[1].as_str().unwrap_or("").trim().to_string(),
            lon: s[5].as_f64()?, lat: s[6].as_f64()?, alt: s[7].as_f64().or(s[13].as_f64()).unwrap_or(0.0),
            vel: s[9].as_f64().filter(|v| *v < 400.0).unwrap_or(0.0), hdg: s[10].as_f64().unwrap_or(0.0), vr: s[11].as_f64().unwrap_or(0.0),
            ..Default::default()
        })
    }).collect();
    (!out.is_empty()).then_some(out)
}

pub fn parse_adsb(v: &Value) -> Option<Vec<Aircraft>> {
    let ac = v["ac"].as_array()?;
    Some(ac.iter().filter_map(|p| {
        if p["alt_baro"].as_str() == Some("ground") { return None; }
        Some(Aircraft {
            hex: p["hex"].as_str()?.to_lowercase(), call: p["flight"].as_str().unwrap_or("").trim().to_string(),
            lat: p["lat"].as_f64()?, lon: p["lon"].as_f64()?, alt: p["alt_baro"].as_f64().unwrap_or(0.0) * 0.3048,
            vel: p["gs"].as_f64().unwrap_or(0.0) * 0.514444, hdg: p["track"].as_f64().or(p["true_heading"].as_f64()).unwrap_or(0.0),
            vr: p["baro_rate"].as_f64().unwrap_or(0.0) * 0.00508, kind: p["t"].as_str().map(String::from), reg: p["r"].as_str().map(String::from),
            squawk: p["squawk"].as_str().map(String::from), mach: p["mach"].as_f64(),
        })
    }).collect())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn opensky_skips_ground_and_missing_position() {
        let v = serde_json::json!({"states": [
            ["abc", "BAW1  ", "UK", 0, 0, -0.5, 51.4, 10000.0, false, 250.0, 90.0, 0.0, null, 10100.0],
            ["def", "GND1", "UK", 0, 0, -0.5, 51.4, 0.0, true, 0.0, 0.0, 0.0, null, 0.0],
            ["ghi", "NOPOS", "UK", 0, 0, null, null, 0.0, false, 0.0, 0.0, 0.0, null, 0.0]]});
        let l = parse_opensky(&v).unwrap();
        assert_eq!(l.len(), 1); assert_eq!(l[0].call, "BAW1"); assert_eq!(l[0].lat, 51.4);
    }
    #[test]
    fn adsb_converts_units() {
        let v = serde_json::json!({"ac": [{"hex": "4D24C0", "flight": "X ", "lat": 1.0, "lon": 2.0, "alt_baro": 10000, "gs": 100.0, "track": 5.0}]});
        let l = parse_adsb(&v).unwrap(); assert_eq!(l[0].hex, "4d24c0"); assert!((l[0].alt - 3048.0).abs() < 0.1);
    }
}
