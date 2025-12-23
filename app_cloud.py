#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATLAS OBSIDIAN VEIL - Cloud Application
Servidor completo para hospedagem em Render.com
"""

from flask import Flask, jsonify, send_file, send_from_directory, Response
import sqlite3
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

DB_PATH = 'data/obsidian_veil_cloud.db'

def get_db():
    """Conectar ao banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Página inicial"""
    return send_file('ABRIR_DASHBOARD.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard principal"""
    return send_file('ABRIR_DASHBOARD.html')

@app.route('/extraterrestre')
def extraterrestre():
    """Painel de candidatos extraterrestres"""
    return send_file('PAINEL_EXTRATERRESTRE.html')

@app.route('/cards')
def cards():
    """Cards padronizados"""
    return send_file('CARDS_PADRONIZADOS.html')

@app.route('/analise-profunda')
def analise_profunda():
    """Análise profunda cards"""
    return send_file('ANALISE_PROFUNDA_CARDS.html')

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/status')
def api_status():
    """Status do sistema"""
    conn = get_db()
    cur = conn.cursor()
    
    # Total de anomalias
    cur.execute("SELECT COUNT(*) as total FROM anomalies")
    total_anomalias = cur.fetchone()['total']
    
    # Level 3 (score 75)
    cur.execute("SELECT COUNT(*) as total FROM anomalies WHERE anomaly_score = 75.0")
    level3 = cur.fetchone()['total']
    
    # Score >= 95
    cur.execute("SELECT COUNT(*) as total FROM anomalies WHERE anomaly_score >= 95.0")
    ultra_rare = cur.fetchone()['total']
    
    conn.close()
    
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "system": "Atlas Obsidian Veil",
        "stats": {
            "total_anomalies": total_anomalias,
            "level3_events": level3,
            "ultra_rare_events": ultra_rare
        }
    })

@app.route('/api/level3')
def api_level3():
    """Dados Level 3 (score 75)"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, timestamp_utc, geo_tag, anomaly_score, 
               anomaly_level, packet_size, protocol_info
        FROM anomalies
        WHERE anomaly_score = 75.0 AND anomaly_level = 3
        ORDER BY timestamp_utc DESC
        LIMIT 200
    """)
    
    eventos = []
    for row in cur.fetchall():
        eventos.append({
            "id": row['id'],
            "timestamp_utc": row['timestamp_utc'],
            "geo_tag": row['geo_tag'],
            "anomaly_score": row['anomaly_score'],
            "anomaly_level": row['anomaly_level'],
            "packet_size": row['packet_size'],
            "protocol_info": json.loads(row['protocol_info']) if row['protocol_info'] else {}
        })
    
    conn.close()
    
    return jsonify({
        "total": len(eventos),
        "classification": "RARE_SIGNAL (Level 3)",
        "score": 75.0,
        "events": eventos
    })

@app.route('/api/ultra-rare')
def api_ultra_rare():
    """Dados Ultra Rare (score >= 95)"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, timestamp_utc, geo_tag, anomaly_score, 
               anomaly_level, packet_size, protocol_info,
               structural_analysis, pattern_analysis
        FROM anomalies
        WHERE anomaly_score >= 95.0
        ORDER BY anomaly_score DESC, timestamp_utc DESC
    """)
    
    eventos = []
    for row in cur.fetchall():
        eventos.append({
            "id": row['id'],
            "timestamp_utc": row['timestamp_utc'],
            "geo_tag": row['geo_tag'],
            "anomaly_score": row['anomaly_score'],
            "anomaly_level": row['anomaly_level'],
            "packet_size": row['packet_size'],
            "protocol_info": json.loads(row['protocol_info']) if row['protocol_info'] else {},
            "structural_analysis": json.loads(row['structural_analysis']) if row['structural_analysis'] else {},
            "pattern_analysis": json.loads(row['pattern_analysis']) if row['pattern_analysis'] else {}
        })
    
    conn.close()
    
    return jsonify({
        "total": len(eventos),
        "classification": "ULTRA_RARE / NON_HUMAN (Level 4+)",
        "score_threshold": 95.0,
        "events": eventos
    })

@app.route('/api/recent')
def api_recent():
    """Eventos recentes (últimas 100 anomalias)"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, timestamp_utc, geo_tag, anomaly_score, 
               anomaly_level, packet_size
        FROM anomalies
        ORDER BY timestamp_utc DESC
        LIMIT 100
    """)
    
    eventos = []
    for row in cur.fetchall():
        eventos.append({
            "id": row['id'],
            "timestamp_utc": row['timestamp_utc'],
            "geo_tag": row['geo_tag'],
            "anomaly_score": row['anomaly_score'],
            "anomaly_level": row['anomaly_level'],
            "packet_size": row['packet_size']
        })
    
    conn.close()
    
    return jsonify({
        "total": len(eventos),
        "events": eventos
    })

@app.route('/api/stats')
def api_stats():
    """Estatísticas gerais"""
    conn = get_db()
    cur = conn.cursor()
    
    # Total por nível
    cur.execute("""
        SELECT anomaly_level, COUNT(*) as count
        FROM anomalies
        GROUP BY anomaly_level
        ORDER BY anomaly_level
    """)
    
    levels = {}
    for row in cur.fetchall():
        levels[f"level_{row['anomaly_level']}"] = row['count']
    
    # Top localizações
    cur.execute("""
        SELECT geo_tag, COUNT(*) as count
        FROM anomalies
        GROUP BY geo_tag
        ORDER BY count DESC
        LIMIT 10
    """)
    
    top_locations = []
    for row in cur.fetchall():
        top_locations.append({
            "location": row['geo_tag'],
            "count": row['count']
        })
    
    # Score médio
    cur.execute("SELECT AVG(anomaly_score) as avg_score FROM anomalies")
    avg_score = cur.fetchone()['avg_score']
    
    conn.close()
    
    return jsonify({
        "levels": levels,
        "top_locations": top_locations,
        "average_score": round(avg_score, 2) if avg_score else 0
    })

@app.route('/api/seti-candidates')
def api_seti_candidates():
    """Candidatos extraterrestres (análise SETI)"""
    try:
        with open('candidatos_extraterrestres.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({
            "error": "SETI analysis not run yet",
            "message": "Run detector_extraterrestre.py first"
        }), 404

@app.route('/health')
def health():
    """Health check para Render"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
