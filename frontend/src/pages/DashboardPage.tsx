import React, { useEffect, useState } from 'react';
import { Camera, CheckCircle, AlertTriangle, Leaf } from 'lucide-react';
import { apiService } from '../services/api';
import { DashboardStats } from '../types';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiService.getStats()
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(console.error);
  }, []);

  if (loading || !stats) {
    return <div className="py-20 text-center text-sm text-slate-500">Loading farm analytics...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Diagnostics Dashboard</h1>
        <p className="text-slate-600 text-sm mt-1">Live aggregate statistics calculated from recorded field leaf inspections.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {[
          { label: 'Total Leaf Scans', val: stats.total_scans, icon: Camera },
          { label: 'Healthy Foliage', val: stats.healthy_count, icon: CheckCircle },
          { label: 'Diseased Detections', val: stats.diseased_count, icon: AlertTriangle },
          { label: 'Crops Monitored', val: stats.crop_distribution.length, icon: Leaf },
        ].map(card => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
              <div className="flex justify-between items-center text-slate-500 text-xs font-semibold uppercase">
                <span>{card.label}</span>
                <Icon className="w-4 h-4 text-emerald-600" />
              </div>
              <div className="text-3xl font-extrabold text-slate-900 font-mono">{card.val}</div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">Scans by Crop</h3>
          <div className="space-y-3">
            {stats.crop_distribution.map(c => (
              <div key={c.crop} className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span>{c.crop}</span>
                  <span className="font-mono text-slate-500">{c.total_scans} scans</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden flex">
                  <div
                    className="bg-emerald-500 h-full"
                    style={{ width: `${(c.healthy_scans / (c.total_scans || 1)) * 100}%` }}
                  />
                  <div
                    className="bg-amber-500 h-full"
                    style={{ width: `${(c.diseased_scans / (c.total_scans || 1)) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">Most Frequent Pathogens</h3>
          <div className="space-y-2.5">
            {stats.disease_distribution.map((d, i) => (
              <div key={i} className="flex justify-between p-2.5 rounded-xl bg-slate-50 text-xs">
                <div>
                  <span className="font-bold text-slate-800">{d.disease_name}</span>
                  <span className="text-slate-500 block text-[11px]">{d.crop}</span>
                </div>
                <span className="font-mono font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800 self-center">
                  {d.count} cases
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
