import React, { useEffect, useState } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import { ArrowLeft, Printer, Camera, AlertTriangle, CheckCircle, PhoneCall } from 'lucide-react';
import { apiService } from '../services/api';
import { PredictionResult } from '../types';

export default function ResultPage() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const [result, setResult] = useState<PredictionResult | null>(location.state?.result || null);
  const [loading, setLoading] = useState(!result);
  const [activeTab, setActiveTab] = useState<'symptoms' | 'causes' | 'prevention' | 'management' | 'expert'>('symptoms');

  useEffect(() => {
    if (!result && id) {
      setLoading(true);
      apiService.getHistoryDetail(id)
        .then(data => {
          setResult(data);
          setLoading(false);
        })
        .catch(console.error);
    }
  }, [id]);

  if (loading || !result) {
    return (
      <div className="py-20 text-center text-sm text-slate-500">
        Loading diagnostic findings...
      </div>
    );
  }

  const isHealthy = result.is_healthy;
  const guidance = result.guidance || {};

  return (
    <div id="printable-report" className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="flex items-center justify-between no-print border-b border-slate-200 pb-4">
        <Link to="/detect" className="text-xs font-semibold text-emerald-700 flex items-center gap-1.5">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Scanner</span>
        </Link>
        <div className="flex gap-2">
          <button
            onClick={() => window.print()}
            className="px-3.5 py-1.5 rounded-xl border border-slate-300 text-xs font-semibold text-slate-700 flex items-center gap-1.5"
          >
            <Printer className="w-4 h-4" />
            <span>Print Report</span>
          </button>
          <Link
            to="/detect"
            className="px-3.5 py-1.5 rounded-xl bg-emerald-600 text-white text-xs font-semibold flex items-center gap-1.5"
          >
            <Camera className="w-4 h-4" />
            <span>Scan Another</span>
          </Link>
        </div>
      </div>

      {result.is_uncertain && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-sm flex gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Elevated Uncertainty Notice:</span>
            <p className="text-xs text-amber-800 mt-0.5">
              {result.ood_warning || "Model confidence score suggests ambiguity. Please verify symptoms in the field."}
            </p>
          </div>
        </div>
      )}

      {/* Main card */}
      <div className="p-8 rounded-3xl bg-white border border-slate-200 shadow-sm grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
        <div className="rounded-2xl overflow-hidden bg-slate-100 border border-slate-200 flex items-center justify-center max-h-72">
          <img src={result.image_url} alt="" className="object-contain max-h-72 w-full" />
        </div>
        <div className="md:col-span-2 space-y-4">
          <div className="flex gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">{result.crop}</span>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${isHealthy ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
              {isHealthy ? 'HEALTHY FOLIAGE' : 'DISEASE DETECTED'}
            </span>
          </div>

          <h2 className="text-3xl font-extrabold text-slate-900">{result.disease_name}</h2>
          {guidance.pathogen && <p className="text-xs text-slate-500 font-mono">Pathogen: {guidance.pathogen}</p>}

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span>Confidence</span>
              <span className="font-mono text-emerald-700">{(result.confidence * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full ${result.confidence > 0.7 ? 'bg-emerald-500' : 'bg-amber-500'}`}
                style={{ width: `${result.confidence * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Guidance tabs */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="flex border-b border-slate-200 bg-slate-50 overflow-x-auto">
          {(['symptoms', 'causes', 'prevention', 'management', 'expert'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 py-3.5 text-xs font-bold uppercase tracking-wider border-b-2 ${
                activeTab === tab ? 'border-emerald-600 text-emerald-700 bg-white' : 'border-transparent text-slate-600'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === 'symptoms' && (
            <ul className="space-y-2 text-sm text-slate-700">
              {(guidance.common_symptoms || []).map((s, idx) => (
                <li key={idx} className="flex gap-2">
                  <span className="text-emerald-600 font-bold">•</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          )}

          {activeTab === 'causes' && (
            <ul className="space-y-2 text-sm text-slate-700">
              {(guidance.contributing_factors || []).map((f, idx) => (
                <li key={idx} className="flex gap-2">
                  <span className="text-amber-600 font-bold">•</span>
                  <span>{f}</span>
                </li>
              ))}
            </ul>
          )}

          {activeTab === 'prevention' && (
            <ul className="space-y-2 text-sm text-slate-700">
              {(guidance.prevention_practices || []).map((p, idx) => (
                <li key={idx} className="flex gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <span>{p}</span>
                </li>
              ))}
            </ul>
          )}

          {activeTab === 'management' && (
            <ul className="space-y-2 text-sm text-slate-700">
              {(guidance.general_management || []).map((m, idx) => (
                <li key={idx} className="flex gap-2">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span>{m}</span>
                </li>
              ))}
            </ul>
          )}

          {activeTab === 'expert' && (
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-1">
              <span className="font-bold text-slate-900 block">Extension Advisory Note:</span>
              <p>{guidance.expert_guidance}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
