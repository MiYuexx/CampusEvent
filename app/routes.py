from flask import Blueprint, jsonify, request, render_template

from .service import RegistrationService

bp = Blueprint("api", __name__)
service = RegistrationService()


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/api/activities", methods=["GET"])
def list_activities():
    keyword = request.args.get("keyword")
    activities = service.list_activities(keyword)
    for item in activities:
        item["stats"] = service.activity_stats(item["activity_id"])
    return jsonify(activities)


@bp.route("/api/activities", methods=["POST"])
def create_activity():
    data = request.get_json(force=True)
    try:
        activity_id = service.create_activity(
            title=data.get("title"),
            category=data.get("category", ""),
            start_at=data.get("start_at", ""),
            location=data.get("location", ""),
            capacity=data.get("capacity"),
            policy_type=data.get("policy_type"),
        )
        return jsonify({"activity_id": activity_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/activities/<int:activity_id>", methods=["GET"])
def get_activity(activity_id):
    activity = service.get_activity(activity_id)
    if not activity:
        return jsonify({"error": "活动不存在"}), 404
    activity["stats"] = service.activity_stats(activity_id)
    activity["registrations"] = service.list_registrations(activity_id)
    return jsonify(activity)


@bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    try:
        registration_id, status = service.register(
            activity_id=data.get("activity_id"),
            student_id=data.get("student_id"),
            student_name=data.get("student_name"),
        )
        return jsonify({"registration_id": registration_id, "status": status}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/registrations/<int:registration_id>/review", methods=["POST"])
def review(registration_id):
    data = request.get_json(force=True)
    try:
        status = service.review(registration_id, approve=bool(data.get("approve")))
        return jsonify({"status": status})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/registrations/<int:registration_id>/cancel", methods=["POST"])
def cancel(registration_id):
    try:
        status = service.cancel(registration_id)
        return jsonify({"status": status})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/api/messages/<student_id>", methods=["GET"])
def messages(student_id):
    return jsonify(service.list_messages(student_id))
