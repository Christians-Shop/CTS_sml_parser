#!/usr/bin/env python3
"""
CTS SML Parser - REST API zur Analyse von Tasmota SML Dump Ausgaben

Dieses Programm ist freie Software: Sie können es unter den Bedingungen der
GNU Affero General Public License, wie von der Free Software Foundation
veröffentlicht, weitergeben und/oder modifizieren, entweder gemäß Version 3
der Lizenz oder (nach Ihrer Option) jeder späteren Version.

Dieses Programm wird in der Hoffnung verteilt, dass es nützlich sein wird, aber
OHNE JEDE GEWÄHRLEISTUNG; sogar ohne die implizite Gewährleistung der
MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK. Siehe die GNU Affero
General Public License für weitere Details.

Sie sollten eine Kopie der GNU Affero General Public License zusammen mit
diesem Programm erhalten haben. Falls nicht, siehe <https://www.gnu.org/licenses/>.

Original Copyright (C) 2022-2025 Andreas Thienemann
Modifiziert von Christians Technikshop GmbH (C) 2025
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sml_decoder import TasmotaSMLParser
import logging
import json
import os

app = Flask(__name__)

# CORS konfigurieren - erlaubt Anfragen von allen Origins
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/": {"origins": "*"},
    r"/license": {"origins": "*"}
})

# Rate Limiting für Spam-Schutz konfigurieren
def get_client_ip():
    """Ermittelt die Client-IP, auch hinter einem Proxy"""
    if request.headers.get("X-Forwarded-For"):
        # Bei mehreren IPs (Proxy-Chain) die erste nehmen
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    elif request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP")
    else:
        return get_remote_address()

limiter = Limiter(
    app=app,
    key_func=get_client_ip,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


@app.errorhandler(429)
def ratelimit_handler(e):
    """Custom error handler für Rate Limit Überschreitungen"""
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Zu viele Anfragen. Bitte versuchen Sie es später erneut.",
        "retry_after": str(e.description)
    }), 429

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


@app.route("/")
def index():
    """Root endpoint providing API information and source code link (AGPL v3 requirement)"""
    return jsonify({
        "name": "CTS SML Parser API",
        "version": "1.0.0",
        "description": "REST API zur Analyse von Tasmota SML Dump Ausgaben",
        "endpoints": {
            "/api/decode": {
                "method": "POST",
                "description": "Dekodiert SML Dump Daten und gibt JSON-Response zurück",
                "content_type": "application/json",
                "body": {
                    "smldump": "string oder array von strings - Die SML Dump Daten"
                }
            },
            "/license": {
                "method": "GET",
                "description": "Zeigt die GNU Affero General Public License v3"
            }
        },
        "license": "GNU Affero General Public License v3",
        "source_code": "https://github.com/Christians-Shop/CTS_sml_parser",
        "original_project": "https://github.com/ixs/tasmota-sml-parser",
        "copyright": {
            "original": "Copyright (C) 2022-2025 Andreas Thienemann",
            "modifications": "Copyright (C) 2025 Christians Technikshop GmbH"
        },
        "license_url": "https://www.gnu.org/licenses/agpl-3.0.html"
    }), 200


@app.route("/api/decode", methods=["POST"])
@limiter.limit("10 per minute")  # Maximal 10 Anfragen pro Minute pro IP
def api_decode():
    """API endpoint to decode SML dump and return JSON response"""
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if "smldump" not in data:
            return jsonify({"error": "Missing 'smldump' field in request body"}), 400
        
        smldump = data["smldump"]
        
        # Handle both string and array input
        if isinstance(smldump, str):
            smldump_lines = smldump.splitlines()
        elif isinstance(smldump, list):
            smldump_lines = smldump
        else:
            return jsonify({"error": "'smldump' must be a string or array of strings"}), 400
        
        smldump_lines = [x.strip() for x in smldump_lines if x.strip()]
        
        if not smldump_lines:
            return jsonify({"error": "Empty SML dump provided"}), 400
        
        tas = TasmotaSMLParser()
        msgs = tas.decode_messages(smldump_lines)
        
        messages = []
        for msg in msgs:
            details = tas.get_message_details(msg)
            messages.append(details)
        
        messages = sorted(messages, key=lambda x: str(x["obis"]))
        
        # Build complete Tasmota meter definition
        tasmota_meter_def = tas.build_full_meter_def(msgs) if msgs else ""
        
        # Get serializable errors
        errors = tas.get_serializable_errors()
        
        response = {
            "messages": messages,
            "tasmota_meter_def": tasmota_meter_def,
            "parse_errors": errors["parse_errors"],
            "obis_errors": errors["obis_errors"]
        }
        
        client_ip = get_client_ip()
        logger.info(
            f'{client_ip} - - - "{request.method} {request.path} {request.scheme}"',
            extra={
                "custom_dimensions": {
                    "remote_addr": client_ip,
                    "path": request.path,
                    "messages_count": len(messages),
                }
            },
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        client_ip = get_client_ip()
        logger.error(f"Error in API decode from {client_ip}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/license")
def license():
    """Route to display the LICENSE file (AGPL v3 requirement)"""
    try:
        with open("LICENSE", "r", encoding="utf-8") as f:
            license_text = f.read()
        return jsonify({
            "license": "GNU Affero General Public License v3",
            "full_text": license_text,
            "source_code": "https://github.com/Christians-Shop/CTS_sml_parser"
        }), 200
    except FileNotFoundError:
        return jsonify({"error": "Lizenzdatei nicht gefunden."}), 404




if __name__ == "__main__":
    logger.info("Startup")
    app.run(debug=True)
