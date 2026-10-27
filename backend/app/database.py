import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.config import settings

_local = threading.local()

def get_connection() -> sqlite3.Connection:
    """Get a thread-local SQLite connection with foreign keys enabled."""
    if not hasattr(_local, "connection") or _local.connection is None:
        conn = sqlite3.connect(
            str(settings.db_path),
            timeout=30.0,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        _local.connection = conn
    return _local.connection

@contextmanager
def transaction():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def init_db():
    """Initialize SQLite database tables and indexes."""
    with transaction() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                crop TEXT NOT NULL,
                disease_name TEXT NOT NULL,
                raw_class_name TEXT NOT NULL,
                display_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                is_healthy INTEGER NOT NULL,
                is_uncertain INTEGER NOT NULL DEFAULT 0,
                uncertainty_score REAL NOT NULL DEFAULT 0.0,
                ood_warning TEXT,
                alternatives_json TEXT NOT NULL DEFAULT '[]',
                guidance_json TEXT NOT NULL DEFAULT '{}',
                processing_time_ms REAL NOT NULL DEFAULT 0.0,
                model_version TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_crop ON scans(crop);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_is_healthy ON scans(is_healthy);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_scans_disease ON scans(disease_name);")

# ----------------- Database Repository Functions -----------------

def insert_scan(scan_data: Dict[str, Any]) -> None:
    with transaction() as conn:
        conn.execute("""
            INSERT INTO scans (
                id, filename, crop, disease_name, raw_class_name, display_name,
                confidence, is_healthy, is_uncertain, uncertainty_score, ood_warning,
                alternatives_json, guidance_json, processing_time_ms, model_version,
                created_at
            ) VALUES (
                :id, :filename, :crop, :disease_name, :raw_class_name, :display_name,
                :confidence, :is_healthy, :is_uncertain, :uncertainty_score, :ood_warning,
                :alternatives_json, :guidance_json, :processing_time_ms, :model_version,
                :created_at
            );
        """, scan_data)

def get_scan_by_id(scan_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    if not row:
        return None
    d = dict(row)
    d["is_healthy"] = bool(d["is_healthy"])
    d["is_uncertain"] = bool(d["is_uncertain"])
    d["alternatives"] = json.loads(d["alternatives_json"])
    d["guidance"] = json.loads(d["guidance_json"])
    d["image_url"] = f"/uploads/{d['filename']}"
    d["thumbnail_url"] = f"/uploads/thumbnails/thumb_{d['filename']}"
    return d

def get_scans(
    limit: int = 50,
    offset: int = 0,
    crop: Optional[str] = None,
    is_healthy: Optional[bool] = None,
    search: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], int]:
    conn = get_connection()
    conditions = []
    params: List[Any] = []

    if crop:
        conditions.append("LOWER(crop) = LOWER(?)")
        params.append(crop)
    if is_healthy is not None:
        conditions.append("is_healthy = ?")
        params.append(1 if is_healthy else 0)
    if search:
        conditions.append("(crop LIKE ? OR disease_name LIKE ? OR display_name LIKE ?)")
        term = f"%{search}%"
        params.extend([term, term, term])

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    count_cursor = conn.execute(f"SELECT COUNT(*) FROM scans {where_clause}", params)
    total_count = count_cursor.fetchone()[0]

    query = f"""
        SELECT id, filename, crop, disease_name, display_name, confidence,
               is_healthy, is_uncertain, created_at
        FROM scans
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?;
    """
    params.extend([limit, offset])
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()

    results = []
    for r in rows:
        d = dict(r)
        d["is_healthy"] = bool(d["is_healthy"])
        d["is_uncertain"] = bool(d["is_uncertain"])
        d["image_url"] = f"/uploads/{d['filename']}"
        d["thumbnail_url"] = f"/uploads/thumbnails/thumb_{d['filename']}"
        results.append(d)

    return results, total_count

def delete_scan_by_id(scan_id: str) -> bool:
    with transaction() as conn:
        cursor = conn.execute("SELECT filename FROM scans WHERE id = ?", (scan_id,))
        row = cursor.fetchone()
        if not row:
            return False
        filename = row["filename"]
        conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))

    # Also clean up image files if they exist
    img_path = settings.uploads_dir / filename
    thumb_path = settings.thumbnails_dir / f"thumb_{filename}"
    if img_path.exists():
        try:
            img_path.unlink()
        except Exception:
            pass
    if thumb_path.exists():
        try:
            thumb_path.unlink()
        except Exception:
            pass
    return True

def clear_scans() -> int:
    with transaction() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM scans;")
        count = cursor.fetchone()[0]
        conn.execute("DELETE FROM scans;")
    return count

def get_dashboard_statistics() -> Dict[str, Any]:
    conn = get_connection()
    total_cursor = conn.execute("SELECT COUNT(*) FROM scans;")
    total_scans = total_cursor.fetchone()[0]

    healthy_cursor = conn.execute("SELECT COUNT(*) FROM scans WHERE is_healthy = 1;")
    healthy_count = healthy_cursor.fetchone()[0]

    diseased_count = total_scans - healthy_count

    uncertain_cursor = conn.execute("SELECT COUNT(*) FROM scans WHERE is_uncertain = 1;")
    uncertain_count = uncertain_cursor.fetchone()[0]

    healthy_pct = round((healthy_count / total_scans * 100.0), 1) if total_scans > 0 else 0.0

    # Crop distribution
    crop_cursor = conn.execute("""
        SELECT crop,
               COUNT(*) as total_scans,
               SUM(CASE WHEN is_healthy = 1 THEN 1 ELSE 0 END) as healthy_scans,
               SUM(CASE WHEN is_healthy = 0 THEN 1 ELSE 0 END) as diseased_scans
        FROM scans
        GROUP BY crop
        ORDER BY total_scans DESC;
    """)
    crop_dist = [dict(r) for r in crop_cursor.fetchall()]

    # Disease distribution (top diseases among diseased scans)
    disease_cursor = conn.execute("""
        SELECT disease_name, crop, COUNT(*) as count
        FROM scans
        WHERE is_healthy = 0
        GROUP BY crop, disease_name
        ORDER BY count DESC
        LIMIT 10;
    """)
    disease_dist = [dict(r) for r in disease_cursor.fetchall()]

    # Recent 10 scans
    recent_scans, _ = get_scans(limit=10, offset=0)

    return {
        "total_scans": total_scans,
        "healthy_count": healthy_count,
        "diseased_count": diseased_count,
        "uncertain_count": uncertain_count,
        "healthy_percentage": healthy_pct,
        "crop_distribution": crop_dist,
        "disease_distribution": disease_dist,
        "recent_activity": recent_scans
    }
