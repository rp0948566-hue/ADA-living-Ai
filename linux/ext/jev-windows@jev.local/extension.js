import Gio from 'gi://Gio';
import Meta from 'gi://Meta';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const XML = `<node><interface name="org.jev.Windows">
<method name="List"><arg type="s" direction="out" name="json"/></method>
<method name="Place"><arg type="u" direction="in" name="id"/><arg type="i" direction="in" name="x"/><arg type="i" direction="in" name="y"/><arg type="i" direction="in" name="w"/><arg type="i" direction="in" name="h"/><arg type="b" direction="out" name="ok"/></method>
<method name="Focus"><arg type="u" direction="in" name="id"/><arg type="b" direction="out" name="ok"/></method>
<method name="Monitors"><arg type="s" direction="out" name="json"/></method>
</interface></node>`;

const wins = () => global.get_window_actors().map(a => a.meta_window).filter(w => w.get_window_type() === Meta.WindowType.NORMAL);
const byId = id => wins().find(w => w.get_id() === id);

export default class JevWindows extends Extension {
    enable() {
        this._impl = Gio.DBusExportedObject.wrapJSObject(XML, {
            List: () => JSON.stringify(wins().map(w => { const r = w.get_frame_rect(); return {
                id: w.get_id(), pid: w.get_pid(), cls: w.get_wm_class() || '', gid: w.get_gtk_application_id() || '',
                title: w.get_title() || '', frame: [r.x, r.y, r.width, r.height], monitor: w.get_monitor(),
                focus: w.has_focus(), min: w.minimized}; })),
            Place: (id, x, y, w, h) => { const win = byId(id); if (!win) return false;
                try { if (win.minimized) win.unminimize(); if (win.is_fullscreen()) win.unmake_fullscreen();
                      if (win.get_maximized()) win.unmaximize(); } catch (e) {}
                win.move_resize_frame(true, x, y, w, h); return true; },
            Focus: id => { const win = byId(id); if (!win) return false;
                if (win.minimized) win.unminimize(); win.activate(global.get_current_time()); return true; },
            Monitors: () => JSON.stringify(global.display.get_n_monitors ? [...Array(global.display.get_n_monitors()).keys()].map(i => {
                const g = global.display.get_monitor_geometry(i); return {i, x: g.x, y: g.y, w: g.width, h: g.height,
                    primary: i === global.display.get_primary_monitor()}; }) : []),
        });
        this._impl.export(Gio.DBus.session, '/org/jev/Windows');
        this._own = Gio.bus_own_name_on_connection(Gio.DBus.session, 'org.jev.Windows', Gio.BusNameOwnerFlags.NONE, null, null);
    }
    disable() {
        this._impl?.unexport(); this._impl = null;
        if (this._own) Gio.bus_unown_name(this._own); this._own = 0;
    }
}
