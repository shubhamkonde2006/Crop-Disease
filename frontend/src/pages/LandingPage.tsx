import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Camera, BookOpen, CheckCircle, Sparkles, Activity, Shield, ArrowRight } from 'lucide-react';
import { apiService } from '../services/api';

export default function LandingPage() {
  const [crops, setCrops] = useState<string[]>([]);

  useEffect(() => {
    apiService.getCrops()
      .then(setCrops)
      .catch(console.error);
  }, []);

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-b from-emerald-50/60 via-white to-slate-50 pt-16 pb-24 border-b border-slate-200 text-center">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 text-xs font-semibold">
            <Sparkles className="w-4 h-4 text-emerald-600" />
            <span>Next-Generation Foliar AI Diagnostics</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Identify Plant Diseases in <span className="text-emerald-600">Seconds</span>
          </h1>

          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Upload leaf images to diagnose crop pathogens with neural computer vision. Access symptoms, biological causes, and verified treatment guidance.
          </p>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3.5">
            <Link
              to="/detect"
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-base shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 transition-all hover:scale-105"
            >
              <Camera className="w-5 h-5" />
              <span>Detect Disease Now</span>
            </Link>
            <Link
              to="/knowledge"
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-semibold text-base border border-slate-300 shadow-sm flex items-center justify-center gap-2"
            >
              <BookOpen className="w-5 h-5 text-slate-500" />
              <span>Explore Disease Catalog</span>
            </Link>
          </div>

          <div className="pt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-500">
            <div className="flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-emerald-600" />
              <span className="font-medium text-slate-700">14 Major Crops</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-emerald-600" />
              <span className="font-medium text-slate-700">38 Disease Profiles</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-emerald-600" />
              <span className="font-medium text-slate-700">MobileNetV3 PyTorch Engine</span>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs uppercase font-bold tracking-widest text-emerald-600 mb-2">Simple Workflow</h2>
            <h3 className="text-3xl font-extrabold text-slate-900">How AgriShield Works</h3>
            <p className="text-slate-600 mt-2 text-sm">Three easy steps to move from an affected plant leaf to an actionable management plan.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: '01', title: 'Capture or Upload Leaf', desc: 'Snap a clear leaf photo in natural daylight or pick an image file.', icon: Camera },
              { step: '02', title: 'Neural Vision Analysis', desc: 'PyTorch MobileNetV3 classifies foliar lesions and evaluates calibrated entropy.', icon: Activity },
              { step: '03', title: 'Actionable Guidance', desc: 'Review biological causes, cultural prevention, and local extension guidance.', icon: Shield },
            ].map(item => {
              const Icon = item.icon;
              return (
                <div key={item.step} className="p-7 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
                  <div className="text-3xl font-extrabold text-emerald-600/30 font-mono">{item.step}</div>
                  <div className="w-10 h-10 rounded-xl bg-white border border-slate-200 text-emerald-600 flex items-center justify-center">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h4 className="text-lg font-bold text-slate-900">{item.title}</h4>
                  <p className="text-sm text-slate-600 leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Supported Crops */}
      <section className="py-20 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-10">
            <div>
              <h2 className="text-xs uppercase font-bold tracking-widest text-emerald-600 mb-1">Supported Crops</h2>
              <h3 className="text-3xl font-extrabold text-slate-900">14 Major Agricultural Commodities</h3>
            </div>
            <Link to="/knowledge" className="mt-3 sm:mt-0 text-sm font-semibold text-emerald-700 hover:text-emerald-800 flex items-center gap-1">
              <span>View All Disease Profiles</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            {(crops.length > 0 ? crops : ['Apple', 'Blueberry', 'Cherry', 'Corn', 'Grape', 'Orange', 'Peach', 'Bell Pepper', 'Potato', 'Raspberry', 'Soybean', 'Squash', 'Strawberry', 'Tomato']).map(c => (
              <div key={c} className="p-4 rounded-xl bg-white border border-slate-200 text-center font-bold text-xs text-slate-800 shadow-sm">
                {c}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
