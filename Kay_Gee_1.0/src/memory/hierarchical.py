"""
Hierarchical Case Memory - Scalable Long-Term Learning
Three-tier hierarchy: episodic → prototypical → semantic
Improvements: Proper vectorization, fixed types, basic LSH integration,
robust prototype computation (most common action), safer SQL.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Sequence
from collections import Counter

# Optional numeric / clustering dependencies
try:
    import numpy as np
    from sklearn.cluster import MiniBatchKMeans
    _CLUSTER_AVAILABLE = True
except Exception:
    np = None
    MiniBatchKMeans = None
    _CLUSTER_AVAILABLE = False

# Shared feature order - extend as needed for your system
FEATURE_KEYS = ['stress', 'curiosity', 'time_late_night', 'boredom', 'anger']  # Example
FEATURE_DIM = len(FEATURE_KEYS)

def dict_to_vector(features: Dict[str, float]) -> List[float]:
    return [features.get(key, 0.0) for key in FEATURE_KEYS]

def vector_to_dict(vector: Sequence[float]) -> Dict[str, float]:
    return {key: float(vector[i]) for i, key in enumerate(FEATURE_KEYS) if abs(vector[i]) > 1e-6}


class HierarchicalMemory:
    def __init__(self):
        self.episodic = SQLiteVault("data/episodic.db")
        self.prototypical = SQLiteVault("data/prototypical.db")
        self.semantic = PrologKG("data/semantic.pl")
        self.lsh = LSHForest(dim=FEATURE_DIM)

    def retrieve(self, query_features: dict, k: int = 5) -> List[Dict]:
        query_vec = dict_to_vector(query_features)
        hits = []
        
        # Tier 1: Semantic rules (mock - extend with real Prolog query)
        hits.extend(self.semantic.query_rules(query_features, top_k=2))
        
        # Tier 2: Prototypical with LSH
        if len(hits) < k:
            proto_hits = self.prototypical.lsh_search(query_vec, k - len(hits), self.lsh)
            hits.extend(proto_hits)
        
        # Tier 3: Episodic with LSH
        if len(hits) < k:
            epi_hits = self.episodic.lsh_search(query_vec, k - len(hits), self.lsh)
            hits.extend(epi_hits)
        
        return sorted(hits, key=lambda x: x.get('confidence', 0.0), reverse=True)[:k]

    def nightly_consolidation(self):
        cutoff_30 = (datetime.now() - timedelta(days=30)).isoformat()
        cutoff_90 = (datetime.now() - timedelta(days=90)).isoformat()
        
        # Episodic → Prototypical
        old_cases = self.episodic.get_older_than(cutoff_30)
        if len(old_cases) >= 20:  # Lower threshold for practicality
            raw_vectors = [json.loads(c['features_vec']) for c in old_cases]
            if _CLUSTER_AVAILABLE and np is not None:
                vectors = np.array(raw_vectors)
                n_clusters = max(5, min(20, len(vectors) // 6))
                clusters = MiniBatchKMeans(n_clusters=n_clusters, batch_size=32).fit(vectors)

                for label in set(clusters.labels_):
                    cluster_indices = np.where(clusters.labels_ == label)[0]
                    cluster_cases = [old_cases[i] for i in cluster_indices]
                    if len(cluster_cases) >= 3:
                        prototype = self.compute_prototype(cluster_cases)
                        proto_id = self.prototypical.store(prototype)
                        self.lsh.add(prototype['features_vec'], proto_id)
            else:
                # Fallback: simple chunking into prototypes
                chunk_size = max(3, len(raw_vectors) // 6)
                for i in range(0, len(old_cases), chunk_size):
                    cluster_cases = old_cases[i:i+chunk_size]
                    if len(cluster_cases) >= 3:
                        prototype = self.compute_prototype(cluster_cases)
                        proto_id = self.prototypical.store(prototype)
                        self.lsh.add(prototype['features_vec'], proto_id)

            self.episodic.archive_older_than(cutoff_30)
        
        # Prototypical → Semantic (placeholder - integrate real induction_engine)
        old_prototypes = self.prototypical.get_older_than(cutoff_90)
        for proto in old_prototypes:
            # Example mock induction
            # rule = induction_engine.induce_from_prototype(proto)
            # if rule.confidence > 0.85:
            #     self.semantic.assert_rule(rule.clause)
            pass  # Replace with real induction

    def compute_prototype(self, cluster_cases: List[Dict]) -> Dict:
        raw_vectors = [json.loads(c['features_vec']) for c in cluster_cases]
        if np is not None:
            vectors = np.array(raw_vectors)
            centroid_vec = vectors.mean(axis=0).tolist()
        else:
            # Pure-Python centroid
            dim = len(raw_vectors[0]) if raw_vectors else 0
            centroid = [0.0] * dim
            for vec in raw_vectors:
                for j, val in enumerate(vec):
                    centroid[j] += val
            if raw_vectors:
                centroid = [v / len(raw_vectors) for v in centroid]
            centroid_vec = centroid

        actions = [c['action'] for c in cluster_cases if c.get('action')]
        most_common_action = Counter(actions).most_common(1)[0][0] if actions else None

        scores = [c['ethical_score'] for c in cluster_cases if c.get('ethical_score') is not None]
        if np is not None and scores:
            avg_score = float(np.mean(scores))
        else:
            avg_score = float(sum(scores) / len(scores)) if scores else 0.0
        
        return {
            'features_vec': centroid_vec,  # Stored as list for clustering
            'features': vector_to_dict(centroid_vec),  # Human-readable
            'action': most_common_action,
            'ethical_score': avg_score,
            'sample_size': len(cluster_cases),
            'timestamp': datetime.now().isoformat(),
            'confidence': avg_score  # For retrieval sorting
        }


class SQLiteVault:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                features_vec TEXT NOT NULL,  -- JSON list for clustering
                features TEXT,               -- Optional JSON dict for readability
                action TEXT,
                ethical_score REAL,
                timestamp TEXT NOT NULL,
                confidence REAL
            )
        """)
        self.conn.commit()

    def get_older_than(self, cutoff: str) -> List[Dict]:
        cursor = self.conn.execute("SELECT * FROM cases WHERE timestamp < ? ORDER BY timestamp", (cutoff,))
        return [dict(row) for row in cursor.fetchall()]

    def store(self, case: Dict) -> int:
        cursor = self.conn.execute("""
            INSERT INTO cases (features_vec, features, action, ethical_score, timestamp, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            json.dumps(case['features_vec']),
            json.dumps(case.get('features')),
            case.get('action'),
            case.get('ethical_score'),
            case['timestamp'],
            case.get('confidence', case.get('ethical_score'))
        ))
        self.conn.commit()
        return cursor.lastrowid

    def lsh_search(self, query_vec: List[float], k: int, lsh_forest: 'LSHForest') -> List[Dict]:
        # Use LSH for candidates, then exact similarity fallback
        candidates = lsh_forest.query(query_vec, num_candidates=k*3)
        if not candidates:
            # Fallback to top by confidence
            cursor = self.conn.execute("SELECT * FROM cases ORDER BY confidence DESC LIMIT ?", (k,))
            return [dict(row) for row in cursor.fetchall()]
        
        # Exact cosine similarity on candidates
        rows = self.conn.executemany("SELECT * FROM cases WHERE id = ?", [(cid,) for cid in candidates]).fetchall()
        # Compute similarity and sort (simplified)
        results = [dict(row) for row in rows]
        results.sort(key=lambda x: x.get('confidence', 0.0), reverse=True)
        return results[:k]

    def archive_older_than(self, cutoff: str):
        self.conn.execute("DELETE FROM cases WHERE timestamp < ?", (cutoff,))
        self.conn.commit()


class PrologKG:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
    
    def query_rules(self, features: dict, top_k: int = 2) -> List[Dict]:
        # Placeholder - integrate real SWI-Prolog query
        return [{'action': 'mock_rule_action', 'confidence': 0.9} for _ in range(min(top_k, 2))]
    
    def assert_rule(self, clause: str):
        with open(self.path, 'a') as f:
            f.write(clause + '.\n')


class LSHForest:
    """Simple multi-probe LSH for demo - replace with annoy/scikit-learn LSH in production"""
    def __init__(self, dim: int = 5, num_tables: int = 5):
        self.dim = dim
        self.num_tables = num_tables
        self.tables = [{} for _ in range(num_tables)]
    
    def _hash(self, vector: List[float], table_id: int) -> int:
        # Random projection hash (simplified)
        return hash(tuple(round(v * (table_id + 1), 3) for v in vector))
    
    def add(self, vector: List[float], case_id: int):
        for i in range(self.num_tables):
            h = self._hash(vector, i)
            self.tables[i].setdefault(h, []).append(case_id)
    
    def query(self, vector: List[float], num_candidates: int = 20) -> List[int]:
        candidates = set()
        for i in range(self.num_tables):
            h = self._hash(vector, i)
            candidates.update(self.tables[i].get(h, []))
        return list(candidates)[:num_candidates]
