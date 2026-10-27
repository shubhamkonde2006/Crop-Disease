import {
  DashboardStats,
  DiseaseInfoItem,
  ModelInfoResponse,
  PredictionResult,
  SampleLeaf,
  ScanHistoryItem
} from '../types';

const API_BASE = '/api/v1';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMsg = `Server error (${response.status})`;
    try {
      const errData = await response.json();
      if (errData.detail) {
        errorMsg = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      } else if (errData.message) {
        errorMsg = errData.message;
      }
    } catch {
      // Keep default errorMsg
    }
    throw new Error(errorMsg);
  }
  return response.json();
}

export const apiService = {
  async predictCrop(file: File, crop?: string): Promise<PredictionResult> {
    const formData = new FormData();
    formData.append('file', file);
    if (crop && crop.trim()) {
      formData.append('crop', crop.trim());
    }

    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      body: formData
    });
    return handleResponse<PredictionResult>(res);
  },

  async predictSample(sampleId: string, crop?: string): Promise<PredictionResult> {
    const res = await fetch(`${API_BASE}/predict/sample`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sample_id: sampleId, crop })
    });
    return handleResponse<PredictionResult>(res);
  },

  async getSamples(): Promise<SampleLeaf[]> {
    const res = await fetch(`${API_BASE}/samples`);
    return handleResponse<SampleLeaf[]>(res);
  },

  async getHistory(params?: {
    limit?: number;
    offset?: number;
    crop?: string;
    isHealthy?: boolean;
    search?: string;
  }): Promise<{ items: ScanHistoryItem[]; total: number }> {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', String(params.limit));
    if (params?.offset) query.set('offset', String(params.offset));
    if (params?.crop) query.set('crop', params.crop);
    if (params?.isHealthy !== undefined) query.set('is_healthy', String(params.isHealthy));
    if (params?.search) query.set('search', params.search);

    const res = await fetch(`${API_BASE}/history?${query.toString()}`);
    return handleResponse<{ items: ScanHistoryItem[]; total: number }>(res);
  },

  async getHistoryDetail(id: string): Promise<PredictionResult> {
    const res = await fetch(`${API_BASE}/history/${id}`);
    return handleResponse<PredictionResult>(res);
  },

  async deleteHistoryItem(id: string): Promise<boolean> {
    const res = await fetch(`${API_BASE}/history/${id}`, {
      method: 'DELETE'
    });
    const data = await handleResponse<{ success: boolean }>(res);
    return data.success;
  },

  async clearHistory(): Promise<boolean> {
    const res = await fetch(`${API_BASE}/history`, {
      method: 'DELETE'
    });
    const data = await handleResponse<{ success: boolean }>(res);
    return data.success;
  },

  async getStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/stats`);
    return handleResponse<DashboardStats>(res);
  },

  async getDiseases(query?: string, crop?: string): Promise<DiseaseInfoItem[]> {
    const searchParams = new URLSearchParams();
    if (query) searchParams.set('query', query);
    if (crop) searchParams.set('crop', crop);

    const res = await fetch(`${API_BASE}/diseases?${searchParams.toString()}`);
    return handleResponse<DiseaseInfoItem[]>(res);
  },

  async getCrops(): Promise<string[]> {
    const res = await fetch(`${API_BASE}/crops`);
    return handleResponse<string[]>(res);
  },

  async getModelInfo(): Promise<ModelInfoResponse> {
    const res = await fetch(`${API_BASE}/model-info`);
    return handleResponse<ModelInfoResponse>(res);
  },

  async getHealth(): Promise<{ status: string; version: string }> {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse<{ status: string; version: string }>(res);
  }
};
