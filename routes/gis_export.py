"""
GIS Export Routes for CARA Risk Assessment Data

This module provides Flask routes for downloading risk assessment data
in CSV and GeoJSON formats for use in ArcGIS and other GIS platforms.
"""

import os
import io
import csv
import logging
from datetime import datetime
from flask import Blueprint, send_file, jsonify, request, abort, Response
from werkzeug.exceptions import NotFound

from core import db
from models import ExportJob
from utils.gis_export import CARAGISExporter
from utils.security_manager import require_same_origin_or_api_key

logger = logging.getLogger(__name__)


def _classify_risk_level(score: float) -> str:
    """Return the qualitative risk level label for a PHRAT score (0–1)."""
    if score >= 0.85:
        return "Critical"
    elif score >= 0.70:
        return "Very High"
    elif score >= 0.55:
        return "High"
    elif score >= 0.40:
        return "Moderate"
    else:
        return "Low"


# Create blueprint for GIS export routes
gis_export_bp = Blueprint('gis_export', __name__, url_prefix='/api/gis')

@gis_export_bp.route('/export/all', methods=['GET', 'POST'])
@require_same_origin_or_api_key('write')
def export_all_data():
    """
    Synchronously generate CSV export for all jurisdiction risk data.
    Returns the CSV file directly as a download.
    """
    try:
        logger.info("Starting synchronous GIS CSV export for all jurisdictions")
        
        from utils.jurisdictions_code import jurisdictions
        from utils.data_processor import process_risk_data
        from utils.jurisdiction_mapping_code import jurisdiction_mapping

        exporter = CARAGISExporter()
        all_data = []

        for j in jurisdictions:
            try:
                jid = j['id']
                # process_risk_data computes the authoritative PHRAT 7-domain score.
                # All domain scores and total_risk_score are taken directly from this
                # result to ensure the CSV export is consistent with the dashboard.
                risk_data = process_risk_data(jid)

                county_name = jurisdiction_mapping.get(jid, 'Unknown')
                centroid = exporter._get_jurisdiction_centroid(county_name)
                natural_hazards = risk_data.get('natural_hazards', {})

                natural_hazards_risk = risk_data.get('natural_hazards_risk', 0.3)
                health_risk = risk_data.get('health_risk', 0.3)
                active_shooter_risk = risk_data.get('active_shooter_risk', 0.2)
                extreme_heat_risk = risk_data.get('extreme_heat_risk', 0.2)
                air_quality_risk = risk_data.get('air_quality_risk', 0.2)
                dam_failure_risk = risk_data.get('dam_failure_risk', 0.1)
                vbd_risk = risk_data.get('vector_borne_disease_risk', 0.1)
                utilities_risk = risk_data.get('utilities', {}).get('overall', 0.2)

                total_score = float(risk_data.get('total_risk_score', 0))
                risk_level = _classify_risk_level(total_score)

                record = {
                    'jurisdiction_id': jid,
                    'jurisdiction': j['name'],
                    'county': county_name,
                    'fips_code': exporter._get_county_fips_code(county_name) or '',
                    'total_risk_score': round(total_score, 4),
                    'risk_level': risk_level,
                    'natural_hazards_risk': round(float(natural_hazards_risk or 0), 4),
                    'health_risk': round(float(health_risk or 0), 4),
                    'active_shooter_risk': round(float(active_shooter_risk or 0), 4),
                    'extreme_heat_risk': round(float(extreme_heat_risk or 0), 4),
                    'air_quality_risk': round(float(air_quality_risk or 0), 4),
                    'dam_failure_risk': round(float(dam_failure_risk or 0), 4),
                    'vector_borne_disease_risk': round(float(vbd_risk or 0), 4),
                    'utilities_risk': round(float(utilities_risk or 0), 4),
                    'flood_risk': round(float(natural_hazards.get('flood', 0) if isinstance(natural_hazards, dict) else 0), 4),
                    'tornado_risk': round(float(natural_hazards.get('tornado', 0) if isinstance(natural_hazards, dict) else 0), 4),
                    'winter_storm_risk': round(float(natural_hazards.get('winter_storm', 0) if isinstance(natural_hazards, dict) else 0), 4),
                    'thunderstorm_risk': round(float(natural_hazards.get('thunderstorm', 0) if isinstance(natural_hazards, dict) else 0), 4),
                    'lat': centroid.get('lat', 44.5),
                    'lon': centroid.get('lon', -89.5),
                    'calculation_timestamp': datetime.now().isoformat(),
                    'framework_version': '2.5',
                    'data_source': 'CARA'
                }
                all_data.append(record)
            except Exception as e:
                logger.warning(f"Failed to process jurisdiction {j['id']}: {e}")

        if not all_data:
            return jsonify({'error': 'No data was generated', 'success': False}), 500

        output = io.StringIO()
        fieldnames = list(all_data[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)

        csv_bytes = output.getvalue().encode('utf-8')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'cara_risk_scores_{timestamp}.csv'

        logger.info(f"Synchronous CSV export complete: {len(all_data)} jurisdictions")

        return Response(
            csv_bytes,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        logger.error(f"Error in synchronous GIS export: {e}")
        return jsonify({
            'error': 'Failed to generate export',
            'message': str(e)
        }), 500

@gis_export_bp.route('/download/csv/<filename>', methods=['GET'])
def download_csv(filename):
    """
    Download a specific CSV export file.
    
    Args:
        filename: Name of the CSV file to download
    """
    try:
        from werkzeug.utils import secure_filename
        
        # Sanitize filename to prevent path traversal
        safe_filename = secure_filename(filename)
        if not safe_filename or safe_filename != filename:
            logger.warning(f"Invalid filename rejected: {filename}")
            abort(400, description="Invalid filename")
        
        # Reject any path separators
        if '/' in filename or '\\' in filename or '..' in filename:
            logger.warning(f"Path traversal attempt rejected: {filename}")
            abort(400, description="Invalid filename")
        
        # Validate filename and path
        if not safe_filename.endswith('.csv'):
            abort(400, description="Invalid file type. Only CSV files are supported.")
        
        # Construct file path
        export_dir = 'exports'
        file_path = os.path.join(export_dir, safe_filename)
        
        # Ensure resolved path is within exports directory
        real_file_path = os.path.realpath(file_path)
        real_export_dir = os.path.realpath(export_dir)
        if not real_file_path.startswith(real_export_dir):
            logger.warning(f"Path traversal attempt blocked: {filename} -> {real_file_path}")
            abort(403, description="Access denied")
        
        if not os.path.exists(real_file_path):
            logger.warning(f"Requested CSV file not found: {real_file_path}")
            abort(404, description="Export file not found. Please regenerate the export.")
        
        logger.info(f"Serving CSV download: {filename}")
        
        return send_file(
            real_file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='text/csv'
        )
        
    except NotFound:
        raise
    except Exception as e:
        logger.error(f"Error serving CSV file {filename}: {e}")
        abort(500, description="Error retrieving export file")

@gis_export_bp.route('/download/geojson/<filename>', methods=['GET'])
def download_geojson(filename):
    """
    Download a specific GeoJSON export file.
    
    Args:
        filename: Name of the GeoJSON file to download
    """
    try:
        from werkzeug.utils import secure_filename
        
        # Sanitize filename to prevent path traversal
        safe_filename = secure_filename(filename)
        if not safe_filename or safe_filename != filename:
            logger.warning(f"Invalid filename rejected: {filename}")
            abort(400, description="Invalid filename")
        
        # Reject any path separators
        if '/' in filename or '\\' in filename or '..' in filename:
            logger.warning(f"Path traversal attempt rejected: {filename}")
            abort(400, description="Invalid filename")
        
        # Validate filename and path
        if not safe_filename.endswith('.geojson'):
            abort(400, description="Invalid file type. Only GeoJSON files are supported.")
        
        # Construct file path
        export_dir = 'exports'
        file_path = os.path.join(export_dir, safe_filename)
        
        # Ensure resolved path is within exports directory
        real_file_path = os.path.realpath(file_path)
        real_export_dir = os.path.realpath(export_dir)
        if not real_file_path.startswith(real_export_dir):
            logger.warning(f"Path traversal attempt blocked: {filename} -> {real_file_path}")
            abort(403, description="Access denied")
        
        if not os.path.exists(real_file_path):
            logger.warning(f"Requested GeoJSON file not found: {real_file_path}")
            abort(404, description="Export file not found. Please regenerate the export.")
        
        logger.info(f"Serving GeoJSON download: {filename}")
        
        return send_file(
            real_file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/geo+json'
        )
        
    except NotFound:
        raise
    except Exception as e:
        logger.error(f"Error serving GeoJSON file {filename}: {e}")
        abort(500, description="Error retrieving export file")

@gis_export_bp.route('/export/jurisdiction/<jurisdiction_id>', methods=['GET', 'POST'])
@require_same_origin_or_api_key('write')
def export_single_jurisdiction(jurisdiction_id):
    """
    Start an asynchronous export job for a single jurisdiction.
    
    Args:
        jurisdiction_id: ID of the jurisdiction to export
    """
    try:
        logger.info(f"Starting async export job for jurisdiction: {jurisdiction_id}")
        
        # Create new export job for single jurisdiction
        job = ExportJob(
            export_type='single_jurisdiction',
            status='queued',
            cache_freshness_minutes=30,
            params={'jurisdiction_id': jurisdiction_id}
        )
        
        db.session.add(job)
        db.session.commit()
        
        logger.info(f"Created single jurisdiction export job {job.id} for {jurisdiction_id}")
        
        return jsonify({
            'status': 'job_created',
            'job_id': str(job.id),
            'jurisdiction_id': jurisdiction_id,
            'message': f'Export job started for {jurisdiction_id}. Use the job_id to check progress.',
            'status_url': f"/api/gis/jobs/{job.id}/status",
            'estimated_duration_seconds': 30
        })
        
    except Exception as e:
        logger.error(f"Error creating export job for jurisdiction {jurisdiction_id}: {e}")
        return jsonify({
            'error': 'Failed to create export job',
            'message': 'An internal error occurred. Please try again.'
        }), 500

@gis_export_bp.route('/fields', methods=['GET'])
def get_export_fields():
    """
    Get information about available fields in the export data.
    """
    field_info = {
        'identifier_fields': {
            'jurisdiction_id': 'Unique identifier for the jurisdiction',
            'jurisdiction': 'Full name of the health department or jurisdiction',
            'county': 'Wisconsin county name',
            'fips_code': 'Federal Information Processing Standard county code'
        },
        'risk_domain_scores': {
            'total_risk_score': 'Overall composite PHRAT score (0.0-1.0); quadratic mean of 7 weighted domains',
            'risk_level': 'Qualitative classification: Low (<0.40), Moderate (0.40-0.54), High (0.55-0.69), Very High (0.70-0.84), Critical (>=0.85)',
            'natural_hazards_risk': 'Combined natural hazards score — equal-weighted mean of flood, tornado, winter storm, thunderstorm EVR scores',
            'health_risk': 'Health metrics / infectious disease risk score',
            'active_shooter_risk': 'Community violence risk assessment',
            'extreme_heat_risk': 'Heat-related health risk score',
            'air_quality_risk': 'Air pollution and quality risk',
            'dam_failure_risk': 'Dam failure risk score (EVR framework, WI DNR / NID inventory)',
            'vector_borne_disease_risk': 'Vector-borne disease risk (Lyme + West Nile Virus, WI DHS surveillance)',
            'utilities_risk': 'Critical infrastructure risk (supplementary — not in PHRAT)'
        },
        'natural_hazard_subtypes': {
            'flood_risk': 'Flood EVR score — NRI 45%, storm events 25%, NFIP claims 10%, water proximity 20%; urban stormwater factor applied to SE WI counties',
            'tornado_risk': 'Tornado EVR score with mobile home density adjustment',
            'winter_storm_risk': 'Winter storm EVR score',
            'thunderstorm_risk': 'Thunderstorm risk from NOAA Storm Events county severity index'
        },
        'geographic_data': {
            'lat': 'Latitude of jurisdiction centroid',
            'lon': 'Longitude of jurisdiction centroid'
        },
        'metadata': {
            'calculation_timestamp': 'When the risk scores were calculated',
            'framework_version': 'CARA framework version used',
            'data_source': 'Source system identifier'
        }
    }
    
    return jsonify({
        'field_descriptions': field_info,
        'total_fields': sum(len(category) for category in field_info.values()),
        'arcgis_compatibility': 'All fields are UTF-8 encoded and ArcGIS compatible',
        'coordinate_system': 'WGS84 (EPSG:4326)'
    })

@gis_export_bp.route('/jobs', methods=['POST'])
@require_same_origin_or_api_key('write')
def create_export_job():
    """
    Create a new export job (alternative endpoint).
    """
    return export_all_data()

@gis_export_bp.route('/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """
    Get the status of an export job.
    
    Args:
        job_id: UUID of the export job
    """
    try:
        job = db.session.query(ExportJob).filter(ExportJob.id == job_id).first()
        
        if not job:
            return jsonify({
                'error': 'Job not found'
            }), 404
        
        response_data = job.to_dict()
        
        # Add download URLs if job is completed
        if job.status == 'completed' and job.result_files:
            base_url = request.host_url.rstrip('/')
            
            downloads = {}
            if 'csv' in job.result_files:
                downloads['csv'] = {
                    'filename': os.path.basename(job.result_files['csv']),
                    'download_url': f"{base_url}/api/gis/download/csv/{os.path.basename(job.result_files['csv'])}",
                    'description': 'Risk scores in tabular CSV format'
                }
            
            if 'geojson' in job.result_files:
                downloads['geojson'] = {
                    'filename': os.path.basename(job.result_files['geojson']),
                    'download_url': f"{base_url}/api/gis/download/geojson/{os.path.basename(job.result_files['geojson'])}",
                    'description': 'Risk scores with spatial geometries'
                }
            
            response_data['downloads'] = downloads
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error getting job status for {job_id}: {e}")
        return jsonify({
            'error': 'Error retrieving job status',
            'message': 'An internal error occurred. Please try again.'
        }), 500

@gis_export_bp.route('/jobs/<job_id>/cancel', methods=['POST'])
@require_same_origin_or_api_key('write')
def cancel_job(job_id):
    """
    Cancel an export job.
    
    Args:
        job_id: UUID of the export job
    """
    try:
        job = db.session.query(ExportJob).filter(ExportJob.id == job_id).first()
        
        if not job:
            return jsonify({
                'error': 'Job not found'
            }), 404
        
        if job.status in ['completed', 'failed', 'canceled']:
            return jsonify({
                'error': f'Cannot cancel job in {job.status} status'
            }), 400
        
        job.status = 'canceled'
        job.finished_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Job canceled successfully',
            'job_id': str(job.id)
        })
        
    except Exception as e:
        logger.error(f"Error canceling job {job_id}: {e}")
        return jsonify({
            'error': 'Error canceling job',
            'message': 'An internal error occurred. Please try again.'
        }), 500

@gis_export_bp.route('/status', methods=['GET'])
def export_status():
    """
    Get general status information about export system.
    """
    try:
        # Get recent jobs
        recent_jobs = db.session.query(ExportJob).order_by(
            ExportJob.created_at.desc()
        ).limit(10).all()
        
        # Get export directory info
        export_dir = 'exports'
        files = []
        if os.path.exists(export_dir):
            for filename in os.listdir(export_dir):
                if filename.endswith(('.csv', '.geojson')):
                    file_path = os.path.join(export_dir, filename)
                    file_stats = os.stat(file_path)
                    
                    files.append({
                        'filename': filename,
                        'size_bytes': file_stats.st_size,
                        'created': file_stats.st_mtime,
                        'type': 'CSV' if filename.endswith('.csv') else 'GeoJSON'
                    })
        
        return jsonify({
            'status': 'Export system operational',
            'recent_jobs': [job.to_dict() for job in recent_jobs],
            'available_files': sorted(files, key=lambda x: x['created'], reverse=True)[:20],
            'total_files': len(files)
        })
        
    except Exception as e:
        logger.error(f"Error checking export status: {e}")
        return jsonify({
            'error': 'Error checking export status',
            'message': 'An internal error occurred. Please try again.'
        }), 500