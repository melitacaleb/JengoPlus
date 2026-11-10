from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

def _sum(qs):
    return qs.aggregate(s=Sum("amount"))["s"] or Decimal("0")

class User(AbstractUser):
    ADMIN, SUPERVISOR = "admin", "supervisor"
    role = models.CharField(max_length=12, choices=[(ADMIN, "Administrator"), (SUPERVISOR, "Supervisor")], default=SUPERVISOR)
    phone = models.CharField(max_length=20, blank=True)

class Project(models.Model):
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=200, blank=True)
    expected_workers = models.PositiveIntegerField(default=0, help_text="Planned daily headcount (0 = not set)")
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class ProjectAssignment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="assignments")
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={"role": "supervisor"})
    class Meta: unique_together = ("project", "supervisor")
    def __str__(self): return f"{self.supervisor} @ {self.project}"

class Worker(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self): return f"{self.code} - {self.name}"

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    supervisor = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={"role": "supervisor"})
    title = models.CharField(max_length=160)
    target = models.CharField(max_length=120, blank=True, help_text="e.g. 200 m of wall")
    deadline = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=12, default="open", choices=[("open", "Open"), ("review", "Completion review"), ("done", "Complete")])
    def __str__(self): return f"{self.title} ({self.project})"
    # Financial measures (concept paper s.9) -- kept separate on purpose
    @property
    def funds_confirmed(self): return _sum(self.disbursement_set.filter(confirmed=True))
    @property
    def approved(self): return _sum(self.expenseclaim_set.filter(status="approved"))
    @property
    def pending(self): return _sum(self.expenseclaim_set.filter(status="submitted"))
    @property
    def returned(self): return _sum(self.fundreturn_set.all())
    @property
    def budget_remaining(self): return self.budget - self.approved
    @property
    def held(self): return self.funds_confirmed - self.approved - self.returned

class Disbursement(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=6, choices=[("mpesa", "M-Pesa"), ("bank", "Bank")])
    reference = models.CharField(max_length=40, unique=True)  # duplicate references blocked
    recipient = models.CharField(max_length=120)
    authorized_by = models.ForeignKey(User, null=True, editable=False, on_delete=models.PROTECT)
    confirmed = models.BooleanField(default=False, help_text="Tick only after checking the M-Pesa/bank statement")
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.reference} {self.amount}"

class FundReturn(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=40, blank=True)
    created = models.DateTimeField(auto_now_add=True)

class ExpenseClaim(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="claims")
    category = models.CharField(max_length=20, choices=[(c, c.title()) for c in ["materials", "labour", "transport", "equipment", "other"]])
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    payee = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    receipt = models.FileField(upload_to="receipts/%Y/%m/")
    status = models.CharField(max_length=10, default="submitted", choices=[("submitted", "Submitted"), ("approved", "Approved"), ("rejected", "Rejected")])
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="reviews")
    reason = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    def clean(self):
        if self.reviewed_by_id and self.reviewed_by_id == self.submitted_by_id:
            raise ValidationError("Nobody can review their own claim.")

class AttendanceSession(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    supervisor = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateField()
    submitted = models.BooleanField(default=False)
    class Meta: unique_together = ("project", "date")
    @property
    def headcount(self): return self.records.count()
    @property
    def over_expected(self): return bool(self.project.expected_workers) and self.headcount > self.project.expected_workers

class AttendanceRecord(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT)
    photo = models.ImageField(upload_to="attendance/%Y/%m/")
    captured_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ("session", "worker")  # DB-level duplicate prevention

class ProgressReport(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT)
    quantity_done = models.CharField(max_length=80, blank=True)
    description = models.TextField()
    photo = models.ImageField(upload_to="progress/%Y/%m/")
    created = models.DateTimeField(auto_now_add=True)

class AuditEvent(models.Model):
    actor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=60)
    detail = models.CharField(max_length=250, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created"]

def audit(user, action, detail=""):
    AuditEvent.objects.create(actor=user, action=action, detail=detail)
