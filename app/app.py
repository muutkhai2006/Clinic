import os
from datetime import date, datetime, time

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://clinic_app:password@postgres:5432/clinic_db",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    patient_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Doctor(db.Model):
    __tablename__ = "doctors"
    id = db.Column(db.Integer, primary_key=True)
    doctor_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    room = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Appointment(db.Model):
    __tablename__ = "appointments"
    __table_args__ = (
        UniqueConstraint("doctor_id", "appointment_date", "appointment_time", name="uq_doctor_slot"),
    )
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Đã đặt")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    patient = db.relationship("Patient", backref=db.backref("appointments", cascade="all, delete-orphan"))
    doctor = db.relationship("Doctor", backref=db.backref("appointments", cascade="all, delete-orphan"))


def seed_data():
    if Patient.query.count() == 0:
        db.session.add_all([
            Patient(patient_code="BN001", full_name="Nguyễn Minh Anh", date_of_birth=date(2002, 4, 15), gender="Nữ", phone="0912000001", address="Thái Nguyên"),
            Patient(patient_code="BN002", full_name="Trần Quốc Huy", date_of_birth=date(1998, 11, 2), gender="Nam", phone="0912000002", address="Bắc Ninh"),
            Patient(patient_code="BN003", full_name="Lê Thu Hà", date_of_birth=date(1987, 7, 21), gender="Nữ", phone="0912000003", address="Hà Nội"),
        ])
    if Doctor.query.count() == 0:
        db.session.add_all([
            Doctor(doctor_code="BS001", full_name="BS. Phạm Hoàng Nam", specialty="Nội tổng quát", phone="0988000001", room="P.201"),
            Doctor(doctor_code="BS002", full_name="BS. Nguyễn Lan Hương", specialty="Tim mạch", phone="0988000002", room="P.305"),
            Doctor(doctor_code="BS003", full_name="BS. Đỗ Minh Khoa", specialty="Da liễu", phone="0988000003", room="P.207"),
        ])
    db.session.commit()
    if Appointment.query.count() == 0:
        p = Patient.query.first()
        d = Doctor.query.first()
        if p and d:
            db.session.add(Appointment(
                patient_id=p.id,
                doctor_id=d.id,
                appointment_date=date.today(),
                appointment_time=time(9, 0),
                reason="Khám tổng quát",
                status="Đã đặt",
            ))
            db.session.commit()


@app.get("/health")
def health():
    db.session.execute(db.text("SELECT 1"))
    return {"status": "ok", "database": "ok"}, 200


@app.get("/")
def index():
    today_count = Appointment.query.filter_by(appointment_date=date.today()).count()
    recent = Appointment.query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).limit(5).all()
    return render_template(
        "index.html",
        patient_count=Patient.query.count(),
        doctor_count=Doctor.query.count(),
        appointment_count=Appointment.query.count(),
        today_count=today_count,
        recent=recent,
    )


@app.route("/patients", methods=["GET", "POST"])
def patients():
    edit_id = request.args.get("edit", type=int)
    editing = db.session.get(Patient, edit_id) if edit_id else None
    if request.method == "POST":
        obj_id = request.form.get("id", type=int)
        obj = db.session.get(Patient, obj_id) if obj_id else Patient()
        try:
            obj.patient_code = request.form["patient_code"].strip()
            obj.full_name = request.form["full_name"].strip()
            obj.date_of_birth = date.fromisoformat(request.form["date_of_birth"]) if request.form.get("date_of_birth") else None
            obj.gender = request.form.get("gender") or None
            obj.phone = request.form.get("phone", "").strip() or None
            obj.address = request.form.get("address", "").strip() or None
            if not obj_id:
                db.session.add(obj)
            db.session.commit()
            flash("Đã lưu thông tin bệnh nhân.", "success")
            return redirect(url_for("patients"))
        except Exception as exc:
            db.session.rollback()
            flash(f"Không thể lưu bệnh nhân: {exc}", "danger")
    return render_template("patients.html", patients=Patient.query.order_by(Patient.id).all(), editing=editing)


@app.post("/patients/<int:patient_id>/delete")
def delete_patient(patient_id):
    obj = db.get_or_404(Patient, patient_id)
    db.session.delete(obj)
    db.session.commit()
    flash("Đã xóa bệnh nhân.", "success")
    return redirect(url_for("patients"))


@app.route("/doctors", methods=["GET", "POST"])
def doctors():
    edit_id = request.args.get("edit", type=int)
    editing = db.session.get(Doctor, edit_id) if edit_id else None
    if request.method == "POST":
        obj_id = request.form.get("id", type=int)
        obj = db.session.get(Doctor, obj_id) if obj_id else Doctor()
        try:
            obj.doctor_code = request.form["doctor_code"].strip()
            obj.full_name = request.form["full_name"].strip()
            obj.specialty = request.form["specialty"].strip()
            obj.phone = request.form.get("phone", "").strip() or None
            obj.room = request.form.get("room", "").strip() or None
            if not obj_id:
                db.session.add(obj)
            db.session.commit()
            flash("Đã lưu thông tin bác sĩ.", "success")
            return redirect(url_for("doctors"))
        except Exception as exc:
            db.session.rollback()
            flash(f"Không thể lưu bác sĩ: {exc}", "danger")
    return render_template("doctors.html", doctors=Doctor.query.order_by(Doctor.id).all(), editing=editing)


@app.post("/doctors/<int:doctor_id>/delete")
def delete_doctor(doctor_id):
    obj = db.get_or_404(Doctor, doctor_id)
    db.session.delete(obj)
    db.session.commit()
    flash("Đã xóa bác sĩ.", "success")
    return redirect(url_for("doctors"))


@app.route("/appointments", methods=["GET", "POST"])
def appointments():
    edit_id = request.args.get("edit", type=int)
    editing = db.session.get(Appointment, edit_id) if edit_id else None
    if request.method == "POST":
        obj_id = request.form.get("id", type=int)
        obj = db.session.get(Appointment, obj_id) if obj_id else Appointment()
        try:
            obj.patient_id = int(request.form["patient_id"])
            obj.doctor_id = int(request.form["doctor_id"])
            obj.appointment_date = date.fromisoformat(request.form["appointment_date"])
            obj.appointment_time = time.fromisoformat(request.form["appointment_time"])
            obj.reason = request.form.get("reason", "").strip() or None
            obj.status = request.form.get("status", "Đã đặt")
            if not obj_id:
                db.session.add(obj)
            db.session.commit()
            flash("Đã lưu lịch khám.", "success")
            return redirect(url_for("appointments"))
        except Exception as exc:
            db.session.rollback()
            flash(f"Không thể lưu lịch khám (có thể bác sĩ đã có lịch cùng giờ): {exc}", "danger")
    return render_template(
        "appointments.html",
        appointments=Appointment.query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all(),
        patients=Patient.query.order_by(Patient.full_name).all(),
        doctors=Doctor.query.order_by(Doctor.full_name).all(),
        editing=editing,
    )


@app.post("/appointments/<int:appointment_id>/delete")
def delete_appointment(appointment_id):
    obj = db.get_or_404(Appointment, appointment_id)
    db.session.delete(obj)
    db.session.commit()
    flash("Đã xóa lịch khám.", "success")
    return redirect(url_for("appointments"))


with app.app_context():
    db.create_all()
    seed_data()
