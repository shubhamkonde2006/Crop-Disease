import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Camera, Sparkles, X, AlertTriangle, Info } from 'lucide-react';
import { apiService } from '../services/api';
import { SampleLeaf } from '../types';

export default function DetectionPage() {
  const navigate = useNavigate();
  const [crops, setCrops] = useState<string[]>([]);
  const [samples, setSamples] = useState<SampleLeaf[]>([]);
  const [selectedCrop, setSelectedCrop] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStage, setAnalysisStage] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    apiService.getCrops().then(setCrops).catch(console.error);
    apiService.getSamples().then(setSamples).catch(console.error);
  }, []);

  const handleFile = (file: File) => {
    setErrorMessage(null);
    const valid = ['image/jpeg', 'image/png', 'image/webp'];
    if (!valid.includes(file.type)) {
      setErrorMessage("Unsupported file format. Please upload JPEG, PNG, or WebP.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage("File exceeds 10 MB maximum limit.");
      return;
    }
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const runDetection = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setErrorMessage(null);

    const stages = [
      "Verifying image dimensions & format...",
      "Extracting leaf foliar features...",
      "Running PyTorch MobileNetV3 inference...",
      "Fetching agronomic guidance..."
    ];

    let i = 0;
    setAnalysisStage(stages[0]);
    const interval = setInterval(() => {
      i++;
      if (i < stages.length) setAnalysisStage(stages[i]);
    }, 350);

    try {
      const res = await apiService.predictCrop(selectedFile, selectedCrop);
      clearInterval(interval);
      navigate(`/results/${res.id}`, { state: { result: res } });
    } catch (err: any) {
      clearInterval(interval);
      setIsAnalyzing(false);
      setErrorMessage(err.message || "Failed to analyze leaf.");
    }
  };

  const runSample = async (s: SampleLeaf) => {
    setIsAnalyzing(true);
    setErrorMessage(null);
    setAnalysisStage(`Testing sample: ${s.display_name}...`);

    try {
      const res = await apiService.predictSample(s.id, s.crop);
      navigate(`/results/${res.id}`, { state: { result: res } });
    } catch (err: any) {
      setIsAnalyzing(false);
      setErrorMessage(err.message || "Sample test failed.");
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">AI Crop Disease Scanner</h1>
        <p className="text-slate-600 text-sm mt-1">Upload a leaf photograph or test with one of our sample leaves.</p>
      </div>

      {errorMessage && (
        <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-bold block">Analysis Notice</span>
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-red-500 hover:text-red-700">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          {/* Crop selector */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700">
              Select Crop (Optional Hint)
            </label>
            <select
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-800"
            >
              <option value="">Auto-Detect Crop (Any of 14 supported crops)</option>
              {crops.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Dropzone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragging(false);
              if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
            }}
            className={`p-8 rounded-2xl border-2 border-dashed text-center ${
              isDragging ? 'border-emerald-500 bg-emerald-50/50' : 'border-slate-300 bg-white'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              className="hidden"
            />
            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              className="hidden"
            />

            {!previewUrl ? (
              <div className="space-y-4 py-6">
                <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto border border-emerald-100">
                  <Upload className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Drag & drop leaf photo here</h3>
                  <p className="text-xs text-slate-500 mt-1">Accepts JPEG, PNG, or WebP up to 10 MB</p>
                </div>
                <div className="flex justify-center gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold flex items-center gap-2"
                  >
                    <Upload className="w-4 h-4" />
                    <span>Browse Files</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => cameraInputRef.current?.click()}
                    className="px-5 py-2.5 rounded-xl bg-slate-100 text-slate-800 text-xs font-bold border border-slate-300 flex items-center gap-2"
                  >
                    <Camera className="w-4 h-4 text-slate-600" />
                    <span>Camera (Mobile)</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative max-h-96 rounded-xl bg-slate-100 overflow-hidden flex items-center justify-center">
                  <img src={previewUrl} alt="Preview" className="max-h-96 object-contain" />
                  <button
                    onClick={() => { setSelectedFile(null); setPreviewUrl(null); }}
                    className="absolute top-3 right-3 p-2 rounded-full bg-slate-900/80 text-white"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex justify-between items-center pt-2">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="px-4 py-2 text-xs font-semibold text-slate-700 border border-slate-200 rounded-xl"
                  >
                    Replace Image
                  </button>
                  <button
                    type="button"
                    disabled={isAnalyzing}
                    onClick={runDetection}
                    className="px-6 py-2.5 rounded-xl bg-emerald-600 text-white text-sm font-bold flex items-center gap-2"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>Run AI Disease Analysis</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {isAnalyzing && (
            <div className="p-5 rounded-2xl bg-emerald-950 text-white space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 border-2 border-white/20 border-t-emerald-400 rounded-full animate-spin" />
                <span className="text-xs font-mono">{analysisStage}</span>
              </div>
            </div>
          )}
        </div>

        {/* 1-click samples */}
        <div className="space-y-6">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">1-Click Test Samples</h3>
            <div className="space-y-2">
              {samples.map(s => (
                <div
                  key={s.id}
                  onClick={() => !isAnalyzing && runSample(s)}
                  className="flex items-center gap-3 p-2 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/40 cursor-pointer"
                >
                  <img src={s.image_url} alt="" className="w-12 h-12 rounded-lg object-cover" />
                  <div className="flex-1 min-w-0">
                    <span className="font-bold text-xs text-slate-900 block truncate">{s.display_name}</span>
                    <span className="text-[10px] text-slate-500">{s.crop} · Click to run</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
