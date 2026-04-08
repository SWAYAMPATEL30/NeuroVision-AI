"use client";

import React, { useEffect, useRef, useState } from 'react';
import { Doctor } from '../types/doctor';
import { ArrowRight, Navigation2, ZoomIn, ZoomOut } from 'lucide-react';

interface Props {
  doctors: Doctor[];
  onSelect: (doctor: Doctor) => void;
  userLat?: number;
  userLng?: number;
}

const AVAILABILITY_COLORS: Record<Doctor['availabilityColor'], string> = {
  green: '#22c55e',
  yellow: '#eab308',
  grey: '#64748b',
};

const AVAILABILITY_LABELS: Record<Doctor['availabilityColor'], string> = {
  green: 'Available Today',
  yellow: 'Next 2 Days',
  grey: 'Next Week+',
};

// Default center: Mumbai
const DEFAULT_CENTER: [number, number] = [19.076, 72.8777];
const DEFAULT_ZOOM = 10;

export function DoctorMapView({ doctors, onSelect, userLat, userLng }: Props) {
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const markersRef = useRef<any[]>([]);
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    // Leaflet must be loaded client-side only — it accesses `window`
    if (typeof window === 'undefined' || !mapContainerRef.current) return;
    if (mapRef.current) return; // Already initialized

    import('leaflet').then((L) => {
      // Fix Leaflet's default icon path broken by Next.js bundling
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      });

      const center: [number, number] = userLat && userLng ? [userLat, userLng] : DEFAULT_CENTER;

      const map = L.map(mapContainerRef.current!, {
        center,
        zoom: DEFAULT_ZOOM,
        zoomControl: false, // We'll render custom controls
        attributionControl: true,
      });

      // OpenStreetMap tile layer with dark-style like Carto Dark Matter
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> © <a href="https://carto.com/">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19,
      }).addTo(map);

      // User location marker
      if (userLat && userLng) {
        const userIcon = L.divIcon({
          className: '',
          html: `
            <div style="position:relative;width:20px;height:20px;">
              <div style="position:absolute;inset:0;background:#3b82f6;border-radius:50%;border:3px solid white;box-shadow:0 0 0 4px rgba(59,130,246,0.3);"></div>
              <div style="position:absolute;inset:-4px;background:rgba(59,130,246,0.2);border-radius:50%;animation:ping 1.5s cubic-bezier(0,0,0.2,1) infinite;"></div>
            </div>
          `,
          iconSize: [20, 20],
          iconAnchor: [10, 10],
        });
        L.marker([userLat, userLng], { icon: userIcon })
          .addTo(map)
          .bindTooltip('📍 You are here', { permanent: false, direction: 'top', className: 'synapse-tooltip' });
      }

      mapRef.current = map;
      setMapReady(true);
    });

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // Add/update doctor markers whenever doctors or map change
  useEffect(() => {
    if (!mapRef.current || !mapReady) return;

    import('leaflet').then((L) => {
      // Clear old markers
      markersRef.current.forEach(m => m.remove());
      markersRef.current = [];

      doctors.forEach(doctor => {
        const color = AVAILABILITY_COLORS[doctor.availabilityColor];
        const availLabel = AVAILABILITY_LABELS[doctor.availabilityColor];

        const icon = L.divIcon({
          className: '',
          html: `
            <div style="
              position: relative;
              display: flex;
              align-items: center;
              justify-content: center;
              width: 38px;
              height: 38px;
              background: rgba(15,23,42,0.92);
              border: 2.5px solid ${color};
              border-radius: 50% 50% 50% 0;
              transform: rotate(-45deg);
              box-shadow: 0 4px 15px rgba(0,0,0,0.5);
              cursor: pointer;
              transition: transform 0.2s;
            ">
              <div style="
                transform: rotate(45deg);
                width: 24px;
                height: 24px;
                border-radius: 50%;
                overflow: hidden;
                border: 1.5px solid ${color};
              ">
                <img 
                  src="${doctor.photo}" 
                  style="width:100%;height:100%;object-fit:cover;" 
                  onerror="this.src='https://via.placeholder.com/24x24/1e293b/94a3b8?text=Dr'"
                />
              </div>
              <div style="
                position: absolute;
                top: -4px;
                right: -4px;
                width: 11px;
                height: 11px;
                background: ${color};
                border-radius: 50%;
                border: 2px solid #0f172a;
                transform: rotate(45deg);
              "></div>
            </div>
          `,
          iconSize: [38, 38],
          iconAnchor: [19, 38],
          popupAnchor: [0, -42],
        });

        const popupContent = `
          <div style="
            background: #0f172a;
            color: #f1f5f9;
            border-radius: 16px;
            padding: 14px;
            min-width: 230px;
            font-family: 'Inter', system-ui, sans-serif;
            border: 1px solid rgba(255,255,255,0.08);
          ">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
              <div style="width:44px;height:44px;border-radius:10px;overflow:hidden;flex-shrink:0;border:2px solid ${color};">
                <img src="${doctor.photo}" style="width:100%;height:100%;object-fit:cover;" onerror="this.src='https://via.placeholder.com/44x44/1e293b/94a3b8?text=Dr'"/>
              </div>
              <div style="min-width:0;">
                <div style="font-weight:800;font-size:14px;color:#f1f5f9;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${doctor.name}</div>
                <div style="font-weight:600;font-size:12px;color:#60a5fa;margin-top:2px;">${doctor.specialization}</div>
              </div>
            </div>

            <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;">
              <span style="
                font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;
                padding:3px 8px;border-radius:999px;
                background:${color}22;color:${color};border:1px solid ${color}44;
                display:flex;align-items:center;gap:4px;
              ">
                <span style="width:6px;height:6px;border-radius:50%;background:${color};display:inline-block;"></span>
                ${availLabel}
              </span>
              ${doctor.onlineAvailable ? `<span style="font-size:10px;font-weight:700;text-transform:uppercase;padding:3px 8px;border-radius:999px;background:rgba(59,130,246,0.12);color:#60a5fa;border:1px solid rgba(59,130,246,0.25);">🎥 Online</span>` : ''}
              ${doctor.offlineAvailable ? `<span style="font-size:10px;font-weight:700;text-transform:uppercase;padding:3px 8px;border-radius:999px;background:rgba(100,116,139,0.15);color:#94a3b8;border:1px solid rgba(100,116,139,0.25);">🏥 In-Person</span>` : ''}
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:14px;">
              <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:8px;text-align:center;border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:14px;font-weight:800;color:#fbbf24;">★ ${doctor.avgRating}</div>
                <div style="font-size:9px;text-transform:uppercase;letter-spacing:0.05em;color:#64748b;margin-top:2px;">Rating</div>
              </div>
              <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:8px;text-align:center;border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:14px;font-weight:800;color:#f1f5f9;">${doctor.experience}yr</div>
                <div style="font-size:9px;text-transform:uppercase;letter-spacing:0.05em;color:#64748b;margin-top:2px;">Exp</div>
              </div>
              <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:8px;text-align:center;border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:14px;font-weight:800;color:#f1f5f9;">₹${doctor.consultationFee}</div>
                <div style="font-size:9px;text-transform:uppercase;letter-spacing:0.05em;color:#64748b;margin-top:2px;">Fee</div>
              </div>
            </div>

            <div style="font-size:11px;color:#94a3b8;margin-bottom:12px;display:flex;align-items:flex-start;gap:4px;">
              <span>📍</span>
              <span>${doctor.clinicName}, ${doctor.area}, ${doctor.city}</span>
            </div>

            <button 
              id="book-btn-${doctor.id}"
              onclick="window.__synapseBookDoctor && window.__synapseBookDoctor('${doctor.id}')"
              style="
                width:100%;
                padding:10px;
                background:linear-gradient(135deg,#2563eb,#1d4ed8);
                color:white;
                border:none;
                border-radius:10px;
                font-size:13px;
                font-weight:700;
                cursor:pointer;
                display:flex;
                align-items:center;
                justify-content:center;
                gap:6px;
                transition:all 0.2s;
              "
              onmouseover="this.style.background='linear-gradient(135deg,#3b82f6,#2563eb)'"
              onmouseout="this.style.background='linear-gradient(135deg,#2563eb,#1d4ed8)'"
            >
              Book Appointment →
            </button>
          </div>
        `;

        const marker = L.marker([doctor.lat, doctor.lng], { icon })
          .addTo(mapRef.current)
          .bindPopup(popupContent, {
            className: 'synapse-popup',
            maxWidth: 260,
            closeButton: true,
          });

        marker.on('click', () => {
          setSelectedDoctor(doctor);
        });

        markersRef.current.push(marker);
      });

      // Expose booking callback to popup buttons
      (window as any).__synapseBookDoctor = (doctorId: string) => {
        const doc = doctors.find(d => d.id === doctorId);
        if (doc) onSelect(doc);
      };

      // Fit map to all doctor markers
      if (doctors.length > 0) {
        const bounds = L.latLngBounds(doctors.map(d => [d.lat, d.lng] as [number, number]));
        mapRef.current.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 });
      }
    });
  }, [doctors, mapReady, onSelect]);

  const handleZoomIn = () => mapRef.current?.zoomIn();
  const handleZoomOut = () => mapRef.current?.zoomOut();
  const handleLocate = () => {
    if (userLat && userLng && mapRef.current) {
      mapRef.current.flyTo([userLat, userLng], 13, { animate: true, duration: 1 });
    }
  };

  return (
    <div className="space-y-4">
      {/* Map Container */}
      <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl" style={{ height: 520 }}>
        <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

        {/* Custom Zoom Controls (top-right) */}
        <div className="absolute top-3 right-3 z-[1000] flex flex-col gap-1.5">
          <button
            onClick={handleZoomIn}
            className="w-9 h-9 bg-slate-900/90 hover:bg-slate-800 border border-white/10 rounded-xl flex items-center justify-center text-slate-300 hover:text-white transition-all shadow-lg backdrop-blur-sm"
            title="Zoom in"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleZoomOut}
            className="w-9 h-9 bg-slate-900/90 hover:bg-slate-800 border border-white/10 rounded-xl flex items-center justify-center text-slate-300 hover:text-white transition-all shadow-lg backdrop-blur-sm"
            title="Zoom out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          {userLat && userLng && (
            <button
              onClick={handleLocate}
              className="w-9 h-9 bg-blue-600/90 hover:bg-blue-500 border border-blue-500/40 rounded-xl flex items-center justify-center text-white transition-all shadow-lg backdrop-blur-sm"
              title="My location"
            >
              <Navigation2 className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Legend (bottom-left) */}
        <div className="absolute bottom-3 left-3 z-[1000] bg-slate-900/90 backdrop-blur-md rounded-xl border border-white/10 p-3 shadow-xl">
          <p className="text-[9px] font-bold uppercase tracking-widest text-slate-500 mb-2">Availability</p>
          <div className="space-y-1.5">
            {(Object.entries(AVAILABILITY_COLORS) as [Doctor['availabilityColor'], string][]).map(([key, color]) => (
              <div key={key} className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: color }} />
                <span className="text-[10px] text-slate-300">{AVAILABILITY_LABELS[key]}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Doctor count badge (top-left) */}
        <div className="absolute top-3 left-3 z-[1000]">
          <div className="bg-slate-900/90 backdrop-blur-md border border-white/10 rounded-xl px-3 py-2 text-xs font-bold text-slate-200 shadow-xl">
            🩺 {doctors.length} doctor{doctors.length !== 1 ? 's' : ''} near you
          </div>
        </div>
      </div>

      {/* Popup CSS injected into head */}
      <style>{`
        .synapse-popup .leaflet-popup-content-wrapper {
          background: #0f172a !important;
          border: 1px solid rgba(255,255,255,0.1) !important;
          border-radius: 16px !important;
          box-shadow: 0 25px 50px rgba(0,0,0,0.8) !important;
          padding: 0 !important;
        }
        .synapse-popup .leaflet-popup-content {
          margin: 0 !important;
          border-radius: 16px !important;
          overflow: hidden !important;
        }
        .synapse-popup .leaflet-popup-tip {
          background: #0f172a !important;
        }
        .synapse-popup .leaflet-popup-close-button {
          color: #64748b !important;
          font-size: 18px !important;
          top: 8px !important;
          right: 8px !important;
          z-index: 1 !important;
        }
        .synapse-popup .leaflet-popup-close-button:hover {
          color: #f1f5f9 !important;
        }
        .synapse-tooltip {
          background: #1e293b !important;
          color: #e2e8f0 !important;
          border: 1px solid rgba(255,255,255,0.1) !important;
          border-radius: 8px !important;
          font-size: 12px !important;
          font-weight: 600 !important;
          box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
        }
        .synapse-tooltip::before {
          border-top-color: rgba(255,255,255,0.1) !important;
        }
        .leaflet-control-attribution {
          background: rgba(15,23,42,0.85) !important;
          color: #64748b !important;
          font-size: 9px !important;
          border-radius: 6px 0 0 0 !important;
        }
        .leaflet-control-attribution a {
          color: #60a5fa !important;
        }
      `}</style>

      {/* Doctor Quick Cards below the map */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {doctors.map(doc => {
          const color = AVAILABILITY_COLORS[doc.availabilityColor];
          const availLabel = AVAILABILITY_LABELS[doc.availabilityColor];
          return (
            <button
              key={doc.id}
              onClick={() => {
                onSelect(doc);
                // Also fly map to doctor
                if (mapRef.current) {
                  mapRef.current.flyTo([doc.lat, doc.lng], 14, { animate: true, duration: 0.8 });
                  // Find and open the marker's popup
                  const idx = doctors.indexOf(doc);
                  if (markersRef.current[idx]) {
                    markersRef.current[idx].openPopup();
                  }
                }
              }}
              className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-xl border border-white/5 hover:border-white/15 hover:bg-slate-900/80 transition-all text-left group"
            >
              <div className="relative flex-shrink-0">
                <img
                  src={doc.photo}
                  alt={doc.name}
                  className="w-9 h-9 rounded-lg object-cover"
                  onError={(e) => { (e.target as HTMLImageElement).src = 'https://via.placeholder.com/36x36/1e293b/94a3b8?text=Dr'; }}
                />
                <div
                  className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border border-slate-900"
                  style={{ background: color }}
                />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold text-slate-200 truncate">{doc.name}</p>
                <p className="text-[10px] text-slate-500 truncate">{doc.area}, {doc.city}</p>
              </div>
              <span className="text-[10px] font-bold text-blue-400 group-hover:translate-x-0.5 transition-transform flex-shrink-0">
                →
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
