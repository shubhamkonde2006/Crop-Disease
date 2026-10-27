import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Trash2, Clock } from 'lucide-react';
import { apiService } from '../services/api';
import { ScanHistoryItem } from '../types';

export default function HistoryPage() {
  const [items, setItems] = useState<ScanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchHistory = () => {
    setLoading(true);
    apiService.getHistory({ search: searchTerm })
      .then(res => {
        setItems(res.items);
        setLoading(false);
      })
      .catch(console.error);
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const deleteItem = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    if (confirm("Delete this scan record?")) {
      await apiService.deleteHistoryItem(id);
      fetchHistory();
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Prediction History</h1>
          <p className="text-slate-600 text-sm mt-1">Archived leaf inspection records ({items.length} total)</p>
        </div>
      </div>

      <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm flex gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search crop or disease..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchHistory()}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800"
          />
        </div>
        <button
          onClick={fetchHistory}
          className="px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold"
        >
          Search
        </button>
      </div>

      {loading ? (
        <div className="py-20 text-center text-xs text-slate-500">Loading history...</div>
      ) : items.length === 0 ? (
        <div className="p-12 text-center rounded-3xl bg-white border border-slate-200 space-y-3">
          <Clock className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">No History Records Found</h3>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {items.map(item => (
            <Link
              key={item.id}
              to={`/results/${item.id}`}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:border-emerald-400 transition-all overflow-hidden flex flex-col"
            >
              <div className="relative h-44 bg-slate-100 flex items-center justify-center">
                <img src={item.image_url || item.thumbnail_url} alt="" className="w-full h-full object-cover" />
                <button
                  onClick={(e) => deleteItem(e, item.id)}
                  className="absolute top-3 right-3 p-1.5 rounded-full bg-slate-900/60 text-white hover:bg-red-600"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="p-4 space-y-1">
                <span className="text-[11px] text-slate-500">{item.crop}</span>
                <h4 className="text-sm font-bold text-slate-900">{item.disease_name}</h4>
                <div className="text-[11px] text-slate-500 font-mono pt-1">
                  {(item.confidence * 100).toFixed(1)}% conf
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
