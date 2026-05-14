import {
  Package, Truck, Warehouse, MapPin, Navigation, Clock, ShieldAlert,
  Info, CheckCircle2, Circle, ChevronRight, FileText, Receipt, Boxes,
  ArrowRight, Calendar, User, Globe, BadgeCheck, Fuel, CircleDot,
  AlertTriangle, Phone, Box, Gauge, Banknote, Home,
} from "lucide-react";

const ACCENT = "#6BA5FF";

const fmt = (n) => "₹" + Math.abs(Number(n)).toLocaleString("en-IN", { maximumFractionDigits: 2 });
const fmt0 = (n) => "₹" + Math.abs(Number(n)).toLocaleString("en-IN", { maximumFractionDigits: 0 });

// status → color
const SHIPMENT_STATUS = {
  in_transit:        { color: ACCENT,    label: "In transit" },
  out_for_delivery:  { color: "#5EEAD4", label: "Out for delivery" },
  delivered:         { color: "#86efac", label: "Delivered" },
  exception:         { color: "#fca5a5", label: "Exception" },
  processing:        { color: "#fde047", label: "Processing" },
  customs:           { color: "#fdba74", label: "In customs" },
};

const FLEET_STATUS = {
  en_route:          "#6BA5FF",
  out_for_delivery:  "#5EEAD4",
  loading:           "#fde047",
  idle:              "rgba(255,255,255,0.4)",
  maintenance:       "#fca5a5",
  delivering:        "#5EEAD4",
};

/* ─── TextBlock ────────────────────────────────────────── */
export function TextBlock({ content }) {
  const parts = content.split(/(\*\*[^*]+\*\*)/g);
  return (
    <div
      className="text-sm leading-relaxed px-4 py-2.5 rounded-2xl rounded-tl-md"
      style={{ background: "rgba(255,255,255,0.03)", color: "rgba(255,255,255,0.88)" }}
    >
      {parts.map((p, i) =>
        p.startsWith("**") && p.endsWith("**") ? (
          <strong key={i} className="text-white font-medium">{p.slice(2, -2)}</strong>
        ) : (
          <span key={i}>{p.split("\n").map((line, j, arr) => (
            <span key={j}>{line}{j < arr.length - 1 && <br />}</span>
          ))}</span>
        )
      )}
    </div>
  );
}

/* ─── DisclaimerBlock ──────────────────────────────────── */
export function DisclaimerBlock({ content }) {
  return (
    <div
      className="flex items-start gap-2.5 px-4 py-2.5 rounded-2xl border"
      style={{ background: "rgba(250, 204, 21, 0.04)", borderColor: "rgba(250, 204, 21, 0.18)", color: "rgba(250, 204, 21, 0.85)" }}
    >
      <Info size={14} className="mt-0.5 flex-shrink-0" />
      <div className="text-11 leading-relaxed">{content}</div>
    </div>
  );
}

/* ─── ProhibitedAlertBlock (also used for privacy + social-eng) ─── */
export function ProhibitedAlertBlock({ headline, message, indicators, contact }) {
  return (
    <div
      className="rounded-2xl border-2 p-4 alert-pulse"
      style={{
        background: "linear-gradient(180deg, rgba(248,113,113,0.10), rgba(248,113,113,0.02))",
        borderColor: "rgba(248,113,113,0.4)",
      }}
    >
      <div className="flex items-center gap-2 mb-2">
        <ShieldAlert size={18} style={{ color: "#fca5a5" }} />
        <div className="text-sm font-semibold" style={{ color: "#fca5a5" }}>{headline}</div>
      </div>
      <div className="text-xs leading-relaxed mb-3" style={{ color: "rgba(255,255,255,0.85)" }}>{message}</div>
      <div className="space-y-1 mb-3">
        {indicators.map((it, i) => (
          <div key={i} className="flex items-start gap-2 text-11" style={{ color: "rgba(255,255,255,0.7)" }}>
            <AlertTriangle size={10} style={{ color: "#fca5a5", marginTop: 3, flexShrink: 0 }} />
            <span>{it}</span>
          </div>
        ))}
      </div>
      <div
        className="flex items-start gap-2 px-3 py-2 rounded-lg border"
        style={{ background: "rgba(255,255,255,0.04)", borderColor: "rgba(248,113,113,0.25)" }}
      >
        <Phone size={12} style={{ color: "#fca5a5", marginTop: 2, flexShrink: 0 }} />
        <div>
          <div className="text-11 font-medium" style={{ color: "rgba(255,255,255,0.9)" }}>{contact.label}</div>
          <div className="text-10" style={{ color: "rgba(255,255,255,0.6)" }}>{contact.detail}</div>
        </div>
      </div>
    </div>
  );
}

/* ─── status pill helper ───────────────────────────────── */
function StatusPill({ status, label }) {
  const meta = SHIPMENT_STATUS[status] || { color: "rgba(255,255,255,0.5)", label };
  return (
    <span className="text-9 px-1.5 py-0.5 rounded-full font-medium uppercase tracking-tightest2"
      style={{ background: meta.color + "22", color: meta.color }}>
      {label || meta.label}
    </span>
  );
}

/* ─── ShipmentTrackingBlock (hero) ─────────────────────── */
export function ShipmentTrackingBlock({ shipment: s }) {
  return (
    <div className="rounded-xl border overflow-hidden"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      {/* header */}
      <div className="px-4 py-3 border-b" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Package size={15} style={{ color: ACCENT }} />
            <span className="text-sm font-mono font-medium" style={{ color: "white" }}>{s.tracking_number}</span>
          </div>
          <StatusPill status={s.status} label={s.status_label} />
        </div>
        <div className="flex items-center gap-2 text-11" style={{ color: "rgba(255,255,255,0.6)" }}>
          <span style={{ color: "rgba(255,255,255,0.85)" }}>{s.origin_city}</span>
          <ArrowRight size={11} />
          <span style={{ color: "rgba(255,255,255,0.85)" }}>{s.destination_city}</span>
          <span style={{ color: "rgba(255,255,255,0.3)" }}>·</span>
          <span>{s.service}</span>
          <span style={{ color: "rgba(255,255,255,0.3)" }}>·</span>
          <span>{s.weight_kg} kg</span>
        </div>
      </div>
      {/* eta strip */}
      <div className="px-4 py-2.5 flex items-center justify-between"
        style={{ background: ACCENT + "0C" }}>
        <div className="flex items-center gap-2">
          <Clock size={12} style={{ color: ACCENT }} />
          <span className="text-11" style={{ color: "rgba(255,255,255,0.6)" }}>Estimated delivery</span>
        </div>
        <span className="text-xs font-medium" style={{ color: "white" }}>{s.estimated_delivery}</span>
      </div>
      {/* timeline */}
      <div className="px-4 py-3">
        {s.timeline.map((ev, i) => {
          const last = i === s.timeline.length - 1;
          const dotColor = ev.exception ? "#fca5a5" : ev.done ? ACCENT : "rgba(255,255,255,0.2)";
          return (
            <div key={i} className="flex gap-3">
              <div className="flex flex-col items-center">
                {ev.exception ? (
                  <AlertTriangle size={13} style={{ color: "#fca5a5" }} />
                ) : ev.done ? (
                  <CheckCircle2 size={13} style={{ color: ACCENT }} />
                ) : (
                  <Circle size={13} style={{ color: "rgba(255,255,255,0.2)" }} />
                )}
                {!last && (
                  <div style={{
                    width: 1.5, flex: 1, minHeight: 22,
                    background: ev.done ? ACCENT + "55" : "rgba(255,255,255,0.08)",
                  }} />
                )}
              </div>
              <div className={`pb-3 ${last ? "" : ""}`} style={{ marginTop: -2 }}>
                <div className="text-xs font-medium"
                  style={{ color: ev.exception ? "#fca5a5" : ev.done ? "white" : "rgba(255,255,255,0.45)" }}>
                  {ev.label}
                </div>
                <div className="text-10" style={{ color: "rgba(255,255,255,0.4)" }}>
                  {ev.location} · {ev.timestamp}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── ShipmentListBlock ────────────────────────────────── */
export function ShipmentListBlock({ title, items }) {
  return (
    <div className="space-y-2">
      {title && (
        <div className="text-10 uppercase tracking-tightest2 px-1" style={{ color: "rgba(255,255,255,0.4)" }}>{title}</div>
      )}
      {items.map((s) => (
        <div key={s.id} className="rounded-xl p-3 border"
          style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
          <div className="flex items-start gap-3">
            <div className="rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ width: 40, height: 40, background: ACCENT + "14" }}>
              <Package size={16} style={{ color: ACCENT }} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="text-xs font-mono font-medium" style={{ color: "white" }}>{s.tracking_number}</span>
                <StatusPill status={s.status} label={s.status_label} />
              </div>
              <div className="flex items-center gap-1.5 text-11 mb-1" style={{ color: "rgba(255,255,255,0.7)" }}>
                <span>{s.origin_city}</span>
                <ArrowRight size={10} style={{ color: "rgba(255,255,255,0.35)" }} />
                <span>{s.destination_city}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-10" style={{ color: "rgba(255,255,255,0.45)" }}>
                  {s.service} · {s.weight_kg} kg · {s.package_type}
                </span>
                <span className="text-10" style={{ color: "rgba(255,255,255,0.55)" }}>{s.estimated_delivery}</span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── RouteMapBlock ────────────────────────────────────── */
export function RouteMapBlock({ tracking_number, origin_city, destination_city, nodes }) {
  return (
    <div className="rounded-xl p-4 border"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="flex items-center gap-2 mb-3">
        <Navigation size={14} style={{ color: ACCENT }} />
        <div className="text-10 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.4)" }}>
          Route · {tracking_number}
        </div>
      </div>
      <div className="flex items-stretch">
        {nodes.map((n, i) => {
          const last = i === nodes.length - 1;
          const dotColor = n.exception ? "#fca5a5" : n.done ? ACCENT : "rgba(255,255,255,0.22)";
          const isEndpoint = n.type === "origin" || n.type === "destination";
          return (
            <div key={i} className="flex-1 flex flex-col items-center" style={{ minWidth: 0 }}>
              <div className="flex items-center w-full">
                <div style={{ flex: 1, height: 2, background: i === 0 ? "transparent" : (nodes[i - 1].done ? ACCENT + "55" : "rgba(255,255,255,0.1)") }} />
                {n.exception ? (
                  <AlertTriangle size={isEndpoint ? 15 : 12} style={{ color: dotColor, flexShrink: 0 }} />
                ) : isEndpoint ? (
                  <MapPin size={15} style={{ color: dotColor, flexShrink: 0, fill: n.done ? dotColor + "33" : "transparent" }} />
                ) : (
                  <CircleDot size={12} style={{ color: dotColor, flexShrink: 0 }} />
                )}
                <div style={{ flex: 1, height: 2, background: last ? "transparent" : (n.done ? ACCENT + "55" : "rgba(255,255,255,0.1)") }} />
              </div>
              <div className="text-9 text-center mt-1.5 px-0.5" style={{
                color: n.exception ? "#fca5a5" : n.done ? "rgba(255,255,255,0.85)" : "rgba(255,255,255,0.4)",
                overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: "100%",
              }}>
                {n.label}
              </div>
              <div className="text-9 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.3)" }}>
                {n.type}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── QuoteBlock ───────────────────────────────────────── */
export function QuoteBlock({ quote: q }) {
  const rows = [
    ["Base rate", q.base_rate],
    [`Weight charge (${q.weight_kg} kg)`, q.weight_charge],
    ["Fuel surcharge", q.fuel_surcharge],
    ["GST (18%)", q.gst],
  ];
  return (
    <div className="rounded-xl border overflow-hidden"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="px-4 py-3 border-b" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2">
            <Receipt size={14} style={{ color: ACCENT }} />
            <span className="text-xs font-medium" style={{ color: "white" }}>{q.service_name} quote</span>
          </div>
          <span className="text-10 px-1.5 py-0.5 rounded-full" style={{ background: ACCENT + "1A", color: ACCENT }}>
            {q.zone} zone
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-11" style={{ color: "rgba(255,255,255,0.6)" }}>
          <span>{q.origin}</span>
          <ArrowRight size={10} />
          <span>{q.destination}</span>
          <span style={{ color: "rgba(255,255,255,0.3)" }}>·</span>
          <span>{q.transit}</span>
        </div>
      </div>
      <div className="px-4 py-3 space-y-1.5">
        {rows.map(([label, val], i) => (
          <div key={i} className="flex items-center justify-between text-xs">
            <span style={{ color: "rgba(255,255,255,0.6)" }}>{label}</span>
            <span className="font-mono" style={{ color: "rgba(255,255,255,0.9)" }}>{fmt(val)}</span>
          </div>
        ))}
        <div className="flex items-center justify-between pt-2 mt-1 border-t" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
          <span className="text-xs font-medium" style={{ color: "white" }}>Total estimate</span>
          <span className="text-base font-mono font-medium" style={{ color: ACCENT }}>{fmt(q.total)}</span>
        </div>
      </div>
    </div>
  );
}

/* ─── ServiceOptionsBlock ──────────────────────────────── */
export function ServiceOptionsBlock({ title, items }) {
  return (
    <div className="space-y-2">
      {title && (
        <div className="text-10 uppercase tracking-tightest2 px-1" style={{ color: "rgba(255,255,255,0.4)" }}>{title}</div>
      )}
      {items.map((sv) => (
        <div key={sv.id} className="rounded-xl p-3 border"
          style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex items-center gap-2">
              <div className="rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ width: 36, height: 36, background: ACCENT + "14" }}>
                <Truck size={15} style={{ color: ACCENT }} />
              </div>
              <div>
                <div className="text-sm font-medium" style={{ color: "white" }}>{sv.name}</div>
                <div className="text-10" style={{ color: "rgba(255,255,255,0.5)" }}>{sv.transit}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs font-mono" style={{ color: ACCENT }}>{fmt0(sv.base_rate)}<span className="text-9" style={{ color: "rgba(255,255,255,0.4)" }}> base</span></div>
              <div className="text-10 font-mono" style={{ color: "rgba(255,255,255,0.55)" }}>+{fmt0(sv.per_kg)}/kg</div>
            </div>
          </div>
          <div className="flex flex-wrap gap-1 mb-2">
            {sv.features.map((f, i) => (
              <span key={i} className="text-9 px-1.5 py-0.5 rounded-full"
                style={{ background: "rgba(255,255,255,0.05)", color: "rgba(255,255,255,0.6)" }}>
                {f}
              </span>
            ))}
          </div>
          <div className="flex items-center justify-between pt-2 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
            <span className="text-10" style={{ color: "rgba(255,255,255,0.55)" }}>
              Best for: {sv.best_for} · up to {sv.max_weight_kg} kg
            </span>
            <button className="flex items-center gap-1 text-10 font-medium px-2.5 py-1 rounded-md"
              style={{ background: ACCENT, color: "#0A0A0A" }}>
              Quote <ChevronRight size={10} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── PickupBlock ──────────────────────────────────────── */
export function PickupBlock({ confirmation: c }) {
  return (
    <div className="rounded-xl p-4 border-2"
      style={{
        background: "linear-gradient(180deg, rgba(107,165,255,0.10), rgba(107,165,255,0.02))",
        borderColor: ACCENT + "44",
      }}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Calendar size={15} style={{ color: ACCENT }} />
          <div className="text-sm font-medium" style={{ color: "white" }}>Pickup booking</div>
        </div>
        <span className="text-10 font-mono px-2 py-0.5 rounded-full" style={{ background: "rgba(250,204,21,0.15)", color: "#fde047" }}>
          {c.status}
        </span>
      </div>
      <div className="space-y-1.5 text-xs">
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Pickup ID</span>
          <span className="font-mono" style={{ color: ACCENT }}>{c.pickup_id}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Address</span>
          <span className="text-right" style={{ color: "white", maxWidth: "70%" }}>{c.address}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Window</span>
          <span style={{ color: "white" }}>{c.window}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Service</span>
          <span style={{ color: "white" }}>{c.service}</span>
        </div>
        <div className="flex justify-between gap-3 pt-1.5 border-t" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Estimated items</span>
          <span style={{ color: "white" }}>{c.estimated_items}</span>
        </div>
      </div>
    </div>
  );
}

/* ─── FleetBlock ───────────────────────────────────────── */
export function FleetBlock({ title, items }) {
  return (
    <div className="rounded-xl p-4 border" style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="flex items-center gap-2 mb-3">
        <Truck size={14} style={{ color: ACCENT }} />
        <div className="text-10 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.4)" }}>
          {title || "Fleet status"}
        </div>
      </div>
      <div className="space-y-2">
        {items.map((v) => {
          const sc = FLEET_STATUS[v.status] || "rgba(255,255,255,0.5)";
          return (
            <div key={v.id} className="px-3 py-2.5 rounded-lg" style={{ background: "rgba(255,255,255,0.02)" }}>
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-medium" style={{ color: "white" }}>{v.id}</span>
                  <span className="text-10" style={{ color: "rgba(255,255,255,0.5)" }}>{v.type}</span>
                </div>
                <span className="text-9 px-1.5 py-0.5 rounded-full font-medium uppercase tracking-tightest2"
                  style={{ background: sc + "22", color: sc }}>
                  {v.status_label}
                </span>
              </div>
              <div className="flex items-center justify-between text-10 mb-1.5" style={{ color: "rgba(255,255,255,0.55)" }}>
                <span className="flex items-center gap-1"><User size={9} /> {v.driver}</span>
                <span className="flex items-center gap-1"><MapPin size={9} /> {v.current_location}</span>
              </div>
              {/* load bar */}
              <div className="flex items-center gap-2">
                <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.06)" }}>
                  <div style={{ width: `${v.load_pct}%`, height: "100%", background: v.load_pct > 90 ? "#fca5a5" : ACCENT, borderRadius: 999 }} />
                </div>
                <span className="text-9 font-mono" style={{ color: "rgba(255,255,255,0.5)" }}>
                  {v.load_pct}% · {(v.capacity_kg / 1000).toFixed(1)}t
                </span>
              </div>
              {v.route !== "—" && (
                <div className="flex items-center justify-between text-10 mt-1.5 pt-1.5 border-t" style={{ borderColor: "rgba(255,255,255,0.05)" }}>
                  <span style={{ color: "rgba(255,255,255,0.5)" }}>{v.route}</span>
                  <span style={{ color: "rgba(255,255,255,0.7)" }}>Next: {v.next_stop} · {v.eta}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── WarehouseBlock ───────────────────────────────────── */
export function WarehouseBlock({ title, items }) {
  return (
    <div className="space-y-2">
      {title && (
        <div className="text-10 uppercase tracking-tightest2 px-1" style={{ color: "rgba(255,255,255,0.4)" }}>{title}</div>
      )}
      {items.map((w) => (
        <div key={w.id} className="rounded-xl p-3 border"
          style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex items-center gap-2">
              <div className="rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ width: 36, height: 36, background: ACCENT + "14" }}>
                <Warehouse size={15} style={{ color: ACCENT }} />
              </div>
              <div>
                <div className="text-sm font-medium" style={{ color: "white" }}>{w.name}</div>
                <div className="text-10" style={{ color: "rgba(255,255,255,0.5)" }}>{w.location}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-mono font-medium" style={{ color: w.used_pct > 85 ? "#fca5a5" : ACCENT }}>{w.used_pct}%</div>
              <div className="text-9 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.4)" }}>utilised</div>
            </div>
          </div>
          {/* utilisation bar */}
          <div className="h-1 rounded-full overflow-hidden mb-2" style={{ background: "rgba(255,255,255,0.06)" }}>
            <div style={{ width: `${w.used_pct}%`, height: "100%", background: w.used_pct > 85 ? "#fca5a5" : ACCENT, borderRadius: 999 }} />
          </div>
          <div className="grid grid-cols-3 gap-2 text-10 mb-2">
            <div>
              <div style={{ color: "rgba(255,255,255,0.4)" }}>Inbound</div>
              <div className="font-mono" style={{ color: "#86efac" }}>↓ {w.inbound_today}</div>
            </div>
            <div>
              <div style={{ color: "rgba(255,255,255,0.4)" }}>Outbound</div>
              <div className="font-mono" style={{ color: ACCENT }}>↑ {w.outbound_today}</div>
            </div>
            <div>
              <div style={{ color: "rgba(255,255,255,0.4)" }}>Staff</div>
              <div className="font-mono" style={{ color: "white" }}>{w.staff_on_shift}</div>
            </div>
          </div>
          {/* inventory categories */}
          <div className="space-y-1 pt-2 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
            {w.inventory.map((cat, i) => (
              <div key={i}>
                <div className="flex items-center justify-between text-10 mb-0.5">
                  <span style={{ color: "rgba(255,255,255,0.7)" }}>{cat.name}</span>
                  <span className="font-mono" style={{ color: "rgba(255,255,255,0.5)" }}>
                    {cat.units.toLocaleString("en-IN")} units · {cat.pct}%
                  </span>
                </div>
                <div className="h-0.5 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.05)" }}>
                  <div style={{ width: `${cat.pct}%`, height: "100%", background: cat.pct > 80 ? "#fde047" : ACCENT + "AA", borderRadius: 999 }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── ClaimBlock ───────────────────────────────────────── */
export function ClaimBlock({ confirmation: c }) {
  return (
    <div className="rounded-xl p-4 border"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <FileText size={15} style={{ color: ACCENT }} />
          <div className="text-sm font-medium" style={{ color: "white" }}>Claim record</div>
        </div>
        <span className="text-10 font-mono px-2 py-0.5 rounded-full" style={{ background: "rgba(250,204,21,0.15)", color: "#fde047" }}>
          {c.status}
        </span>
      </div>
      <div className="space-y-1.5 text-xs">
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Claim ID</span>
          <span className="font-mono" style={{ color: ACCENT }}>{c.claim_id}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Tracking number</span>
          <span className="font-mono" style={{ color: "white" }}>{c.tracking_number}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Issue type</span>
          <span style={{ color: "white" }}>{c.issue_type}</span>
        </div>
        <div className="flex justify-between gap-3 pt-1.5 border-t" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Next step</span>
          <span className="text-right" style={{ color: "rgba(255,255,255,0.85)", maxWidth: "70%" }}>{c.next_step}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Resolution ETA</span>
          <span className="text-right" style={{ color: "white", maxWidth: "60%" }}>{c.resolution_eta}</span>
        </div>
      </div>
    </div>
  );
}

/* ─── ProofOfDeliveryBlock ─────────────────────────────── */
export function ProofOfDeliveryBlock({ tracking_number, service, origin_city, destination_city, pod }) {
  return (
    <div className="rounded-xl border overflow-hidden"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="px-4 py-3 flex items-center justify-between"
        style={{ background: "rgba(134,239,172,0.08)" }}>
        <div className="flex items-center gap-2">
          <BadgeCheck size={15} style={{ color: "#86efac" }} />
          <span className="text-sm font-medium" style={{ color: "white" }}>Proof of delivery</span>
        </div>
        <span className="text-9 px-1.5 py-0.5 rounded-full font-medium uppercase tracking-tightest2"
          style={{ background: "rgba(134,239,172,0.18)", color: "#86efac" }}>
          Delivered
        </span>
      </div>
      <div className="px-4 py-3 space-y-1.5 text-xs">
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Tracking number</span>
          <span className="font-mono" style={{ color: "white" }}>{tracking_number}</span>
        </div>
        <div className="flex items-center gap-1.5 text-11" style={{ color: "rgba(255,255,255,0.6)" }}>
          <span>{origin_city}</span><ArrowRight size={10} /><span>{destination_city}</span>
          <span style={{ color: "rgba(255,255,255,0.3)" }}>·</span><span>{service}</span>
        </div>
        <div className="flex justify-between gap-3 pt-1.5 border-t" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Delivered at</span>
          <span style={{ color: "white" }}>{pod.delivered_at}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Received by</span>
          <span style={{ color: "white" }}>{pod.received_by}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Signature</span>
          <span style={{ color: pod.signature ? "#86efac" : "rgba(255,255,255,0.6)" }}>
            {pod.signature ? "✓ Captured" : "Not captured"}
          </span>
        </div>
        <div className="flex justify-between gap-3">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Location note</span>
          <span className="text-right" style={{ color: "rgba(255,255,255,0.85)", maxWidth: "65%" }}>{pod.location_note}</span>
        </div>
      </div>
    </div>
  );
}

/* ─── EtaBlock ─────────────────────────────────────────── */
export function EtaBlock({ result: r }) {
  const lowConf = r.confidence.toLowerCase().startsWith("lower");
  return (
    <div className="rounded-xl p-4 border"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="flex items-center gap-2 mb-3">
        <Clock size={14} style={{ color: ACCENT }} />
        <div className="text-10 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.4)" }}>
          Delivery estimate
        </div>
      </div>
      <div className="flex items-center gap-3 mb-3">
        <div className="rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ width: 48, height: 48, background: ACCENT + "14" }}>
          <Package size={20} style={{ color: ACCENT }} />
        </div>
        <div>
          <div className="text-base font-medium" style={{ color: "white" }}>{r.estimated_delivery}</div>
          <div className="text-11 font-mono" style={{ color: "rgba(255,255,255,0.5)" }}>{r.tracking_number}</div>
        </div>
      </div>
      <div className="space-y-1.5 text-xs">
        <div className="flex justify-between">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Destination</span>
          <span style={{ color: "white" }}>{r.destination_city}</span>
        </div>
        <div className="flex justify-between">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Current location</span>
          <span style={{ color: "white" }}>{r.current_location}</span>
        </div>
        <div className="flex justify-between">
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Status</span>
          <span style={{ color: "white" }}>{r.status_label}</span>
        </div>
        <div className="flex justify-between pt-1.5 border-t" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
          <span style={{ color: "rgba(255,255,255,0.5)" }}>Confidence</span>
          <span style={{ color: lowConf ? "#fca5a5" : "#86efac" }}>{r.confidence}</span>
        </div>
      </div>
    </div>
  );
}

/* ─── CustomsBlock ─────────────────────────────────────── */
export function CustomsBlock({ breakdown: b }) {
  const rows = [
    ["Declared value", b.declared_value],
    ["Duty estimate", b.duty_estimate],
    ["VAT / IGST estimate", b.vat_estimate],
    ["Clearance fee", b.clearance_fee],
  ];
  return (
    <div className="rounded-xl border overflow-hidden"
      style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
      <div className="px-4 py-3 border-b flex items-center gap-2" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
        <Globe size={14} style={{ color: ACCENT }} />
        <span className="text-xs font-medium" style={{ color: "white" }}>Customs estimate — {b.destination}</span>
      </div>
      <div className="px-4 py-3 space-y-1.5">
        {rows.map(([label, val], i) => (
          <div key={i} className="flex items-center justify-between text-xs">
            <span style={{ color: "rgba(255,255,255,0.6)" }}>{label}</span>
            <span className="font-mono" style={{ color: "rgba(255,255,255,0.9)" }}>{fmt(val)}</span>
          </div>
        ))}
        <div className="flex items-center justify-between pt-2 mt-1 border-t" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
          <span className="text-xs font-medium" style={{ color: "white" }}>Total landed cost</span>
          <span className="text-base font-mono font-medium" style={{ color: ACCENT }}>{fmt(b.total_landed_cost)}</span>
        </div>
      </div>
      <div className="px-4 py-3 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
        <div className="text-10 uppercase tracking-tightest2 mb-1.5" style={{ color: "rgba(255,255,255,0.4)" }}>
          Required documents
        </div>
        <div className="space-y-1">
          {b.documents.map((d, i) => (
            <div key={i} className="flex items-start gap-2 text-11" style={{ color: "rgba(255,255,255,0.75)" }}>
              <FileText size={10} style={{ color: ACCENT, marginTop: 2, flexShrink: 0 }} />
              <span>{d}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ─── AddressBookBlock ─────────────────────────────────── */
export function AddressBookBlock({ title, items }) {
  return (
    <div className="space-y-2">
      {title && (
        <div className="text-10 uppercase tracking-tightest2 px-1" style={{ color: "rgba(255,255,255,0.4)" }}>{title}</div>
      )}
      {items.map((a) => (
        <div key={a.id} className="rounded-xl p-3 border"
          style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
          <div className="flex items-start gap-3">
            <div className="rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ width: 38, height: 38, background: ACCENT + "14" }}>
              <Home size={15} style={{ color: ACCENT }} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-xs font-medium" style={{ color: "white" }}>{a.label}</span>
                {a.default && (
                  <span className="text-9 px-1.5 py-0.5 rounded-full font-medium uppercase tracking-tightest2"
                    style={{ background: ACCENT + "22", color: ACCENT }}>Default</span>
                )}
              </div>
              <div className="text-11" style={{ color: "rgba(255,255,255,0.8)" }}>{a.name}</div>
              <div className="text-10" style={{ color: "rgba(255,255,255,0.5)" }}>
                {a.line}, {a.city} — {a.pincode}
              </div>
              <div className="text-10 font-mono mt-0.5" style={{ color: "rgba(255,255,255,0.45)" }}>{a.phone}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── Dispatcher ───────────────────────────────────────── */
export default function Block({ block }) {
  switch (block.type) {
    case "text":               return <TextBlock {...block} />;
    case "disclaimer":         return <DisclaimerBlock {...block} />;
    case "prohibited_alert":   return <ProhibitedAlertBlock {...block} />;
    case "shipment_tracking":  return <ShipmentTrackingBlock {...block} />;
    case "shipment_list":      return <ShipmentListBlock {...block} />;
    case "route_map":          return <RouteMapBlock {...block} />;
    case "quote":              return <QuoteBlock {...block} />;
    case "service_options":    return <ServiceOptionsBlock {...block} />;
    case "pickup":             return <PickupBlock {...block} />;
    case "fleet":              return <FleetBlock {...block} />;
    case "warehouse":          return <WarehouseBlock {...block} />;
    case "claim":              return <ClaimBlock {...block} />;
    case "proof_of_delivery":  return <ProofOfDeliveryBlock {...block} />;
    case "eta":                return <EtaBlock {...block} />;
    case "customs":            return <CustomsBlock {...block} />;
    case "address_book":       return <AddressBookBlock {...block} />;
    default:
      return (
        <div className="text-xs px-3 py-2 rounded-md" style={{ background: "rgba(255,255,255,0.04)", color: "rgba(255,255,255,0.5)" }}>
          [Unknown block type: {block.type}]
        </div>
      );
  }
}
