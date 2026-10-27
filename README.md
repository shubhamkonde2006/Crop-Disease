# AgriShield: AI-Powered Crop Disease Detection System

An enterprise-grade, end-to-end foliar plant pathology web application designed to help farmers, agronomists, and agricultural extension agents identify crop diseases from leaf images, quantify prediction uncertainty, and access scientifically grounded management guidance.

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend Client (React SPA / Mobile)"]
        UI["Modern Web & Mobile UI"]
        Dropzone["Foliar Drag-and-Drop / Camera"]
        Samples["1-Click Test Sample Library"]
        Analytics["Live Farm Analytics Dashboard"]
    end

    subgraph Server["Backend Application (FastAPI REST API)"]
        Router["API Gateway / v1 Routes"]
        Preprocessor["Image Preprocessor & OOD Validator"]
        ModelService["PyTorch Model Service (MobileNetV3)"]
        KB["Curated Disease Knowledge Base (38 Classes)"]
        Repo["SQLite Persistence Repository (WAL Mode)"]
    end

    subgraph Storage["Storage Layer"]
        DB[("SQLite Database: crop_disease.db")]
        Uploads[("Secure Archival & Thumbnails")]
        Weights[("PyTorch Weights: crop_mobilenet_v3.pth")]
    end

    Dropzone -->|POST /api/v1/predict| Router
    Samples -->|POST /api/v1/predict/sample| Router
    Analytics -->|GET /api/v1/stats| Router

    Router --> Preprocessor
    Preprocessor -->|RGB Tensor [1, 3, 224, 224]| ModelService
    ModelService -->|Softmax + Entropy| Router
    ModelService -.-> Weights

    Router --> KB
    Router --> Repo
    Repo --> DB
    Repo --> Uploads
    Router -->|JSON Prediction + Dossier| UI
```

---

## 2. Core Capabilities & Key Features

### A. AI Foliar Diagnosis
- **Transfer Learning Model**: MobileNetV3-Small architecture fine-tuned across 38 PlantVillage classes covering 14 critical agricultural crops.
- **Calibrated Uncertainty Estimation**: Calculates Shannon Entropy ($H(p) = -\sum p_i \ln p_i$) across output class probabilities to flag ambiguous foliar symptoms.
- **Out-of-Distribution (OOD) Guardrails**: Analyzes Excess Green Index ($2G - R - B$) and chromatic variance to detect non-leaf images (blanks, vehicles, faces) and flags camera blur via Laplacian variance.
- **Top-5 Hypotheses Distribution**: Displays alternative candidate diagnoses with confidence scores so users understand model reasoning.

### B. Actionable Agronomic Guidance
- **Scientific Dossiers**: Every condition includes pathogens (fungal, bacterial, viral, acari), characteristic visual markers, and contributing weather conditions (temperature, humidity).
- **Integrated Pest Management (IPM)**: Actionable cultural sanitation, crop rotation, and bio-fungicide suggestions.
- **Extension Disclaimers**: Strict guidance directing farmers to local certified crop advisors (CCA) before spraying regulated chemicals.

### C. Farm History & Real-Time Analytics
- **Live Aggregated Statistics**: Real-time totals, healthy-to-diseased ratios, and pathogen frequencies calculated directly from actual records in SQLite.
- **Filterable Scan History**: Search by crop, disease name, and health status with stored thumbnails and detailed past inspection views.
- **1-Click Preloaded Sample Gallery**: Instant evaluation using curated high-definition leaf images (Tomato Early Blight, Healthy Potato, Corn Common Rust, Apple Scab, etc.).
- **Printable / PDF Export**: Print-ready diagnostic summary sheets for field notes.

---

## 3. Technology Stack

| Layer | Component | Version / Description |
|---|---|---|
| **Frontend** | React + TypeScript | React 18, React Router v6, Tailwind CSS, Lucide Icons |
| **Backend** | Python / FastAPI | FastAPI 0.143, Uvicorn, Pydantic v2 |
| **Machine Learning** | PyTorch / Torchvision | PyTorch 2.13 CPU, Torchvision 0.28, Pillow, NumPy |
| **Database** | SQLite3 | Thread-safe connection pooling, WAL journal mode |
| **Image Storage** | Local Safe Archival | UUID-indexed sanitized storage with 256px thumbnails |

---

## 4. Supported Crops & Benchmark Classes (14 Crops, 38 Classes)

1. **Apple**: Apple Scab, Black Rot, Cedar Apple Rust, Healthy
2. **Blueberry**: Healthy
3. **Cherry**: Powdery Mildew, Healthy
4. **Corn (Maize)**: Common Rust, Gray Leaf Spot, Northern Leaf Blight, Healthy
5. **Grape**: Black Rot, Esca (Black Measles), Leaf Blight (Isariopsis), Healthy
6. **Orange (Citrus)**: Citrus Greening (Huanglongbing)
7. **Peach**: Bacterial Spot, Healthy
8. **Bell Pepper**: Bacterial Spot, Healthy
9. **Potato**: Early Blight, Late Blight, Healthy
10. **Raspberry**: Healthy
11. **Soybean**: Healthy
12. **Squash**: Powdery Mildew
13. **Strawberry**: Leaf Scorch, Healthy
14. **Tomato**: Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Two-Spotted Spider Mite, Target Spot, Yellow Leaf Curl Virus, Tomato Mosaic Virus, Healthy

---

## 5. Quick Start & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.14.2)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### Step 1: Clone or Navigate to the Workspace
```powershell
cd C:\Users\SAMARTH\.gemini\antigravity\scratch\crop-disease-detection
```

### Step 2: Install Python Dependencies (If not already installed)
```powershell
pip install -r backend/requirements.txt
```

### Step 3: Run the Application
```powershell
python run.py
```
*Or double-click `start.bat` on Windows.*

### Step 4: Open in Your Browser
- **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger REST API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 6. API Reference

### Detection & Inference
- `POST /api/v1/predict` (multipart/form-data)
  - `file`: UploadFile (JPEG, PNG, WebP; max 10MB)
  - `crop` (optional): Form string (e.g. "Tomato", "Potato")
- `POST /api/v1/predict/sample` (application/json)
  - Body: `{"sample_id": "tomato_early_blight", "crop": "Tomato"}`
- `GET /api/v1/samples` - Returns list of pre-loaded sample leaves

### History & Persistence
- `GET /api/v1/history?limit=50&offset=0&crop=Tomato&is_healthy=false&search=blight`
- `GET /api/v1/history/{scan_id}`
- `DELETE /api/v1/history/{scan_id}`
- `DELETE /api/v1/history` (Clears all records)

### Knowledge Base & Catalog
- `GET /api/v1/diseases?query=blight&crop=Tomato`
- `GET /api/v1/diseases/{raw_class_name}`
- `GET /api/v1/crops`

### Analytics & System
- `GET /api/v1/stats` - Returns live aggregated distribution metrics
- `GET /api/v1/health` - Health check status
- `GET /api/v1/model-info` - PyTorch model architecture, device, and thresholds

---

## 7. Running Backend Integration Tests

To run the automated test suite verifying all 8 integration vectors:
```powershell
python tests/test_backend.py
```

---

## 8. Responsible AI & Agronomic Disclaimers

> [!IMPORTANT]
> **Advisory Disclaimer:** AgriShield is an observational diagnostic aid built on computer vision transfer learning. Models predict visual correlations from training imagery, which can be affected by field dust, nutrient deficiencies, or atypical weather.
> - Never apply regulated chemical fungicides or pesticides based solely on automated digital classification.
> - Confirm diagnosis through field observation and consultation with your regional university agricultural extension office or Certified Crop Advisor (CCA).
