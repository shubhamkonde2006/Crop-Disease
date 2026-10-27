export interface AlternativePrediction {
  class_id: number;
  raw_class_name: string;
  crop: string;
  disease_name: string;
  display_name: string;
  confidence: number;
  is_healthy: boolean;
}

export interface DiseaseGuidance {
  crop: string;
  disease_name: string;
  pathogen?: string;
  is_healthy: boolean;
  severity: 'low' | 'medium' | 'high' | 'critical';
  common_symptoms: string[];
  contributing_factors: string[];
  prevention_practices: string[];
  general_management: string[];
  expert_guidance: string;
}

export interface PredictionResult {
  id: string;
  image_url: string;
  thumbnail_url: string;
  crop: string;
  disease_name: string;
  raw_class_name: string;
  display_name: string;
  confidence: number;
  is_healthy: boolean;
  is_uncertain: boolean;
  uncertainty_score: number;
  ood_warning?: string | null;
  alternatives: AlternativePrediction[];
  guidance: DiseaseGuidance;
  processing_time_ms: number;
  model_version: string;
  created_at: string;
}

export interface ScanHistoryItem {
  id: string;
  crop: string;
  disease_name: string;
  display_name: string;
  confidence: number;
  is_healthy: boolean;
  is_uncertain: boolean;
  thumbnail_url: string;
  image_url: string;
  created_at: string;
}

export interface CropSummary {
  crop: string;
  total_scans: number;
  healthy_scans: number;
  diseased_scans: number;
}

export interface DiseaseCount {
  disease_name: string;
  crop: string;
  count: number;
}

export interface DashboardStats {
  total_scans: number;
  healthy_count: number;
  diseased_count: number;
  uncertain_count: number;
  healthy_percentage: number;
  crop_distribution: CropSummary[];
  disease_distribution: DiseaseCount[];
  recent_activity: ScanHistoryItem[];
}

export interface SampleLeaf {
  id: string;
  crop: string;
  expected_disease: string;
  display_name: string;
  description: string;
  image_url: string;
}

export interface DiseaseInfoItem extends DiseaseGuidance {
  raw_class_name: string;
  display_name: string;
}

export interface ModelInfoResponse {
  architecture: string;
  device: string;
  num_classes: number;
  confidence_threshold: number;
  uncertainty_threshold: number;
  supported_crops: string[];
  total_classes: number;
  status: string;
  is_demo_mode: boolean;
  weights_path: string;
  description: string;
}
