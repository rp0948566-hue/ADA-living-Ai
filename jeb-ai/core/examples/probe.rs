#[tokio::main]
async fn main() {
    let t = jeb_core::Traffic::from_env();
    let g = t.global().await.expect("global feed");
    println!("global: {} aircraft from {} (stale={})", g.aircraft.len(), g.source, g.stale);
    let n = t.near(34.3, 33.1).await.expect("near feed");
    println!("near Cyprus: {} aircraft from {}; first: {:?}", n.aircraft.len(), n.source, n.aircraft.first().map(|a| (&a.call, &a.kind, &a.reg)));
}
