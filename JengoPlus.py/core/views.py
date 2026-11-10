from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.forms import modelform_factory
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils._os import safe_join
from .models import *

def role(r):
    def deco(f):
        @login_required
        @wraps(f)
        def w(req, *a, **k):
            if req.user.role != r:
                return HttpResponseForbidden("Not allowed")  # enforced server-side
            return f(req, *a, **k)
        return w
    return deco

@login_required
def home(req):
    return redirect("dashboard" if req.user.role == "admin" else "sup_home")

# ---------- Supervisor ----------
@role("supervisor")
def sup_home(req):
    return render(req, "core/sup_home.html", {
        "projects": Project.objects.filter(assignments__supervisor=req.user, active=True),
        "tasks": Task.objects.filter(supervisor=req.user).exclude(status="done")})

@role("supervisor")
def attendance(req, pid):
    project = get_object_or_404(Project, pk=pid, assignments__supervisor=req.user)  # site-level access check
    session, _ = AttendanceSession.objects.get_or_create(project=project, date=timezone.localdate(),
                                                         defaults={"supervisor": req.user})
    if req.method == "POST":
        if session.submitted:
            messages.error(req, "Session already submitted.")
        elif req.POST.get("action") == "submit":
            session.submitted = True; session.save()
            audit(req.user, "attendance_submitted", f"{project} {session.date} headcount={session.headcount}")
            messages.success(req, f"Submitted. Headcount: {session.headcount}")
        elif not req.FILES.get("photo") or not req.POST.get("worker"):
            messages.error(req, "Select a worker and capture a photo.")
        else:
            try:
                with transaction.atomic():
                    AttendanceRecord.objects.create(session=session, worker_id=req.POST["worker"], photo=req.FILES["photo"])
                messages.success(req, "Attendance recorded.")
            except IntegrityError:
                messages.error(req, "That worker is already recorded in this session.")
        return redirect("attendance", pid=pid)
    done = session.records.values_list("worker_id", flat=True)
    return render(req, "core/attendance.html", {"project": project, "session": session,
        "workers": Worker.objects.filter(active=True).exclude(pk__in=done), "records": session.records.select_related("worker")})

FORMS = {"expense": (ExpenseClaim, ["category", "amount", "date", "payee", "description", "receipt"]),
         "progress": (ProgressReport, ["quantity_done", "description", "photo"])}

@role("supervisor")
def submit(req, tid, kind):
    if kind not in FORMS: raise Http404
    task = get_object_or_404(Task, pk=tid, supervisor=req.user)
    model, fields = FORMS[kind]
    Form = modelform_factory(model, fields=fields)
    form = Form(req.POST or None, req.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False); obj.task = task; obj.submitted_by = req.user; obj.save()
        audit(req.user, f"{kind}_submitted", f"task={task.pk} id={obj.pk}")
        messages.success(req, "Submitted.")
        return redirect("sup_home")
    return render(req, "core/form.html", {"form": form, "title": f"{kind.title()} - {task.title}"})

# ---------- Administrator ----------
@role("admin")
def dashboard(req):
    tasks = Task.objects.select_related("project", "supervisor")
    sessions = AttendanceSession.objects.select_related("project", "supervisor").order_by("-date")[:15]
    flags = [f"Task '{t.title}' is over budget (remaining {t.budget_remaining})" for t in tasks if t.budget_remaining < 0]
    flags += [f"Task '{t.title}': supervisor holds {t.held} unresolved" for t in tasks if t.held > 0]
    flags += [f"{s.project} {s.date}: headcount {s.headcount} exceeds planned {s.project.expected_workers}" for s in sessions if s.over_expected]
    flags += [f"{s.project} {s.date}: attendance not yet submitted" for s in sessions if not s.submitted and s.date < timezone.localdate()]
    return render(req, "core/dashboard.html", {"tasks": tasks, "sessions": sessions, "flags": flags,
        "pending": ExpenseClaim.objects.filter(status="submitted").count(), "audit": AuditEvent.objects.all()[:10]})

@role("admin")
def claims(req):
    return render(req, "core/claims.html", {"claims": ExpenseClaim.objects.filter(status="submitted").select_related("task", "submitted_by")})

@role("admin")
def review(req, pk):
    c = get_object_or_404(ExpenseClaim, pk=pk, status="submitted")
    decision, reason = req.POST.get("decision"), req.POST.get("reason", "").strip()
    if req.method != "POST": return redirect("claims")
    if c.submitted_by_id == req.user.id:
        messages.error(req, "You cannot review your own claim.")
    elif decision not in ("approved", "rejected") or (decision == "rejected" and not reason):
        messages.error(req, "Rejections need a reason.")
    else:
        c.status, c.reason, c.reviewed_by = decision, reason, req.user; c.save()
        audit(req.user, f"expense_{decision}", f"claim={c.pk} amount={c.amount} {reason}")
        messages.success(req, f"Claim {decision}.")
    return redirect("claims")

@role("admin")
def session_detail(req, pk):
    s = get_object_or_404(AttendanceSession, pk=pk)
    return render(req, "core/session.html", {"s": s, "records": s.records.select_related("worker")})

@role("admin")
def evidence(req, p):  # private photo/receipt access, admins only
    try: path = safe_join(settings.MEDIA_ROOT, p)
    except Exception: raise Http404
    try: return FileResponse(open(path, "rb"))
    except FileNotFoundError: raise Http404
