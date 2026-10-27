import React, { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { apiService } from '../services/api';
import { DiseaseInfoItem } from '../types';

interface KnowledgePageProps {
  crops?: string[];
}

export default function KnowledgePage({ crops: propsCrops }: KnowledgePageProps) {
  const [diseases, setDiseases] = useState<DiseaseInfoItem[]>([]);
  const [crops, setCrops] = useState<string[]>(propsCrops || []);
  const [selectedCrop, setSelectedCrop] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchDiseases = () => {
    setLoading(true);
    apiService.getDiseases(searchQuery, selectedCrop)
      .then(data => {
        setDiseases(data);
        setLoading(false);
      })
      .catch(console.error);
  };

  useEffect(() => {
    if (!propsCrops || propsCrops.length === 0) {
      apiService.getCrops().then(setCrops).catch(console.error);
    }
  }, [propsCrops]);

  useEffect(() => {
    fetchDiseases();
  }, [selectedCrop]);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Disease Knowledge Base</h1>
        <p className="text-slate-600 text-sm mt-1">Curated agronomic profiles covering 38 conditions across 14 crops.</p>
      </div>

      <div className="space-y-4">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
          <input
            type="text"
            placeholder="Search conditions, symptoms, or pathogens..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchDiseases()}
            className="w-full pl-10 pr-24 py-3 bg-white border border-slate-200 rounded-2xl text-sm"
          />
          <button
            onClick={fetchDiseases}
            className="absolute right-2 top-2 px-4 py-1.5 rounded-xl bg-emerald-600 text-white text-xs font-bold"
          >
            Search
          </button>
        </div>

        <div className="flex gap-1.5 overflow-x-auto pb-2">
          <button
            onClick={() => setSelectedCrop('')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap ${
              selectedCrop === '' ? 'bg-emerald-600 text-white' : 'bg-white text-slate-700 border border-slate-200'
            }`}
          >
            All Crops
          </button>
          {crops.map(c => (
            <button
              key={c}
              onClick={() => setSelectedCrop(c)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap ${
                selectedCrop === c ? 'bg-emerald-600 text-white' : 'bg-white text-slate-700 border border-slate-200'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-xs text-slate-500">Loading catalog...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {diseases.map(d => (
            <div key={d.raw_class_name} className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
              <div className="flex justify-between">
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">{d.crop}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${d.is_healthy ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>
                  {d.is_healthy ? 'Healthy' : 'Diseased'}
                </span>
              </div>
              <h3 className="text-base font-bold text-slate-900">{d.disease_name}</h3>
              {d.pathogen && <p className="text-[11px] text-slate-500 font-mono">{d.pathogen}</p>}
              <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                {(d.common_symptoms && d.common_symptoms[0]) || 'Click to view complete profile.'}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
