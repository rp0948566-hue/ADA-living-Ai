//! `jev`: the native entry point. It is the process the task manager and dock show as "Jev",
//! and the one binary that builds on Linux, macOS and Windows. It finds the Jev brain (Python today)
//! and runs it as a child: `jev` opens the typing box (a minimized Jev window keeps it running in the dock; clicking it opens the box), `jev --toggle` is the hotkey, `jev --quit` stops it.
//! shortcut: the brain is still Python behind this launcher; port modules to Rust one at a time, hands.py first.
use std::{env, path::{Path, PathBuf}, process::{exit, Command}};

fn host_script() -> Option<PathBuf> {
    let exe = env::current_exe().ok()?;
    let mut dirs: Vec<PathBuf> = env::var_os("JEV_HOME").map(PathBuf::from).into_iter().collect();
    // target/release/jev -> launcher -> repo, or an installed copy next to linux/
    for up in 0..5 { dirs.push(exe.ancestors().nth(up + 1)?.to_path_buf()); }
    dirs.into_iter().map(|d| d.join("linux").join("host.py")).find(|p| p.exists())
}

fn python() -> &'static str { if cfg!(windows) { "python" } else { "python3" } }

fn main() {
    let mut args: Vec<String> = env::args().skip(1).collect();
    if args.is_empty() { args.push("--type".into()); } // plain launch = the box (the side pop-up), like the Mac menu-bar click
    if args == ["--version"] { println!("jev {}", env!("CARGO_PKG_VERSION")); return; }
    let Some(host) = host_script() else { eprintln!("jev: cannot find linux/host.py (set JEV_HOME to the Jev folder)"); exit(1); };
    let status = Command::new(python()).arg(Path::new(&host)).args(&args).status();
    match status { Ok(s) => exit(s.code().unwrap_or(1)), Err(e) => { eprintln!("jev: cannot start {}: {e}", python()); exit(1) } }
}
