from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.resume import Resume
from app.services.resume.storage_service import SupabaseStorageService
from app.services.resume.parser_service import ResumeParserService
from app.services.resume.gemini_service import GeminiResumeService
from app.schemas.resume_schemas import UpdateSkillsSchema, ResumeResponseSchema
from marshmallow import ValidationError
import io

resume_bp = Blueprint("resume", __name__, url_prefix="/api/resume")

storage_service = SupabaseStorageService()
gemini_service = GeminiResumeService()
resume_response_schema = ResumeResponseSchema()
update_skills_schema = UpdateSkillsSchema()

ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_EXTENSIONS

@resume_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()

    # 1. Validation - check file is in the request
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file part in the request"
        }), 400

    file = request.files["file"]

    # 2. Validation - check file is selected
    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No selected file"
        }), 400

    # 3. Validation - check file extension
    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": "Invalid file type. Only PDF resumes are allowed."
        }), 400

    # 4. Validation - check file size
    file.seek(0, io.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset stream position

    if size > MAX_FILE_SIZE:
        return jsonify({
            "success": False,
            "message": f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB."
        }), 400

    try:
        # Check if user already has a resume record
        existing_resume = Resume.query.filter_by(user_id=user_id).first()

        # Delete old file from storage if it exists
        if existing_resume and existing_resume.file_path:
            try:
                storage_service.delete_resume(existing_resume.file_path)
            except Exception as e:
                print(f"Warning: could not delete old resume file: {str(e)}")

        # 5. Extract text from PDF using pdfplumber before uploading
        try:
            pdf_stream = io.BytesIO(file.read())
            file.seek(0)  # Reset for upload
            raw_text = ResumeParserService.extract_text(pdf_stream)
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to parse PDF content: {str(e)}"
            }), 400

        # Parse text to extract metadata as heuristic backup
        parsed_data = ResumeParserService.parse_resume(raw_text)

        # Call Gemini Resume Analysis (returns structured candidate metadata and review metrics)
        gemini_data = gemini_service.analyze_resume(raw_text)

        # 6. Upload to Supabase Storage
        file_path, file_url = storage_service.upload_resume(file, user_id, file.filename)

        extracted_name = gemini_data.get("name") or parsed_data.get("name")
        extracted_role = gemini_data.get("role") or parsed_data.get("role")
        extracted_skills = gemini_data.get("skills") or parsed_data.get("skills")
        analysis = gemini_data.get("analysis")

        # 7. Update or Create Resume DB Record
        if existing_resume:
            existing_resume.filename = file.filename
            existing_resume.file_path = file_path
            existing_resume.file_url = file_url
            existing_resume.raw_text = raw_text
            existing_resume.extracted_name = extracted_name
            existing_resume.extracted_role = extracted_role
            existing_resume.extracted_skills = extracted_skills
            existing_resume.analysis = analysis
            db.session.commit()
            resume_record = existing_resume
        else:
            resume_record = Resume(
                user_id=user_id,
                filename=file.filename,
                file_path=file_path,
                file_url=file_url,
                raw_text=raw_text,
                extracted_name=extracted_name,
                extracted_role=extracted_role,
                extracted_skills=extracted_skills,
                analysis=analysis
            )
            db.session.add(resume_record)
            db.session.commit()

        return jsonify({
            "success": True,
            "message": "Resume uploaded and parsed successfully",
            "resume": resume_response_schema.dump(resume_record)
        }), 200

    except ValueError as val_err:
        return jsonify({
            "success": False,
            "message": str(val_err)
        }), 503
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"An error occurred during resume upload: {str(e)}"
        }), 500

@resume_bp.route("/current", methods=["GET"])
@jwt_required()
def get_current_resume():
    user_id = get_jwt_identity()
    resume = Resume.query.filter_by(user_id=user_id).first()
    
    if not resume:
        return jsonify({
            "success": False,
            "message": "No resume found for this user."
        }), 404

    return jsonify({
        "success": True,
        "resume": resume_response_schema.dump(resume)
    }), 200

@resume_bp.route("/skills", methods=["PUT"])
@jwt_required()
def update_skills():
    user_id = get_jwt_identity()
    resume = Resume.query.filter_by(user_id=user_id).first()

    if not resume:
        return jsonify({
            "success": False,
            "message": "No resume found to update."
        }), 404

    data = request.get_json()
    try:
        validated_data = update_skills_schema.load(data)
    except ValidationError as err:
        return jsonify({
            "success": False,
            "errors": err.messages
        }), 400

    try:
        resume.extracted_skills = validated_data["skills"]
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Resume skills updated successfully",
            "resume": resume_response_schema.dump(resume)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"An error occurred during skills update: {str(e)}"
        }), 500

@resume_bp.route("/current", methods=["DELETE"])
@jwt_required()
def delete_resume():
    user_id = get_jwt_identity()
    resume = Resume.query.filter_by(user_id=user_id).first()

    if not resume:
        return jsonify({
            "success": False,
            "message": "No resume found to delete."
        }), 404

    try:
        if resume.file_path:
            try:
                storage_service.delete_resume(resume.file_path)
            except Exception as e:
                print(f"Warning: could not delete resume file: {str(e)}")

        db.session.delete(resume)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Resume deleted successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"An error occurred during resume deletion: {str(e)}"
        }), 500
