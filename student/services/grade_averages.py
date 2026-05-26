"""
Tính và lưu điểm trung bình theo năm học (sau khi admin bấm Tính điểm).

Công thức môn / học kỳ (điểm quy về thang 10 từ score/max_score):
    (15p + BT + 2×GK + 3×CK) / 7

TB học kỳ: trung bình các môn đủ 4 loại điểm đã duyệt (chia cho số môn thực tế).
TB cả năm: (TB HK1 + TB HK2) / 2 — chỉ lưu khi có đủ cả hai học kỳ.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from student.models import (
    Grade,
    Student,
    Subject,
    StudentSubjectSemesterAverage,
    StudentSemesterAverage,
    StudentYearAverage,
)

_ONE_DECIMAL = Decimal('0.1')


def round_average_score(value) -> Decimal:
    """Làm tròn điểm trung bình một chữ số thập phân (nửa lên)."""
    d = value if isinstance(value, Decimal) else Decimal(str(value))
    return d.quantize(_ONE_DECIMAL, rounding=ROUND_HALF_UP)


EXPECTED_SUBJECT_COUNT = 11
EXAM_COMPONENTS = ('Quiz', 'Assignment', 'Midterm', 'Final')


def _to_scale_10(score, max_score) -> Decimal:
    if max_score is None:
        return Decimal('0')
    ms = Decimal(str(max_score))
    if ms <= 0:
        return Decimal('0')
    return (Decimal(str(score)) / ms) * Decimal('10')


def _subject_average_from_grades(q_g, a_g, m_g, f_g) -> Decimal:
    q = _to_scale_10(q_g.score, q_g.max_score)
    a = _to_scale_10(a_g.score, a_g.max_score)
    m = _to_scale_10(m_g.score, m_g.max_score)
    f = _to_scale_10(f_g.score, f_g.max_score)
    return (q + a + Decimal('2') * m + Decimal('3') * f) / Decimal('7')


def build_latest_grade_map(academic_year: str) -> dict[tuple[int, int, str, str], Grade]:
    """Mỗi khóa (student_id, subject_id, semester, exam_type) → bản ghi mới nhất (đã duyệt)."""
    qs = (
        Grade.objects.filter(
            academic_year=academic_year,
            semester__in=('1', '2'),
            is_approved=True,
            exam_type__in=EXAM_COMPONENTS,
        )
        .order_by(
            'student_id',
            'subject_id',
            'semester',
            'exam_type',
            '-created_at',
            '-id',
        )
        .only(
            'student_id',
            'subject_id',
            'semester',
            'exam_type',
            'score',
            'max_score',
            'created_at',
            'id',
        )
    )
    seen: dict[tuple[int, int, str, str], Grade] = {}
    for g in qs.iterator(chunk_size=2000):
        key = (g.student_id, g.subject_id, g.semester, g.exam_type)
        if key not in seen:
            seen[key] = g
    return seen


def compute_and_store_academic_year(academic_year: str) -> dict:
    """
    Xóa snapshot cũ của năm học, tính lại và bulk_create.
    Trả về thống kê đơn giản cho thông báo UI.
    """
    subjects = list(Subject.objects.all().order_by('subject_name'))
    student_ids = list(
        Student.objects.filter(is_active=True).values_list('pk', flat=True)
    )

    grade_map = build_latest_grade_map(academic_year)

    ss_rows: list[StudentSubjectSemesterAverage] = []
    sem_rows: list[StudentSemesterAverage] = []
    semester_by_student: dict[int, dict[str, Decimal]] = {}

    warnings_not_eleven = 0

    with transaction.atomic():
        StudentYearAverage.objects.filter(academic_year=academic_year).delete()
        StudentSemesterAverage.objects.filter(academic_year=academic_year).delete()
        StudentSubjectSemesterAverage.objects.filter(academic_year=academic_year).delete()

        for sid in student_ids:
            semester_by_student[sid] = {}
            for sem in ('1', '2'):
                subject_avgs: list[Decimal] = []
                for subj in subjects:
                    kq = (sid, subj.pk, sem, 'Quiz')
                    ka = (sid, subj.pk, sem, 'Assignment')
                    km = (sid, subj.pk, sem, 'Midterm')
                    kf = (sid, subj.pk, sem, 'Final')
                    if kq not in grade_map or ka not in grade_map or km not in grade_map or kf not in grade_map:
                        continue
                    sub_avg = round_average_score(
                        _subject_average_from_grades(
                            grade_map[kq], grade_map[ka], grade_map[km], grade_map[kf]
                        )
                    )
                    subject_avgs.append(sub_avg)
                    ss_rows.append(
                        StudentSubjectSemesterAverage(
                            student_id=sid,
                            subject=subj,
                            academic_year=academic_year,
                            semester=sem,
                            average_score=sub_avg,
                        )
                    )

                if not subject_avgs:
                    continue

                n_sub = len(subject_avgs)
                if n_sub != EXPECTED_SUBJECT_COUNT:
                    warnings_not_eleven += 1

                sem_avg = round_average_score(
                    sum(subject_avgs, Decimal('0')) / Decimal(str(n_sub))
                )
                semester_by_student[sid][sem] = sem_avg
                sem_rows.append(
                    StudentSemesterAverage(
                        student_id=sid,
                        academic_year=academic_year,
                        semester=sem,
                        average_score=sem_avg,
                        subjects_used=n_sub,
                    )
                )

        year_rows: list[StudentYearAverage] = []
        for sid, sem_map in semester_by_student.items():
            if '1' in sem_map and '2' in sem_map:
                y_avg = round_average_score(
                    (sem_map['1'] + sem_map['2']) / Decimal('2')
                )
                year_rows.append(
                    StudentYearAverage(
                        student_id=sid,
                        academic_year=academic_year,
                        average_score=y_avg,
                    )
                )

        batch = 500
        for i in range(0, len(ss_rows), batch):
            StudentSubjectSemesterAverage.objects.bulk_create(ss_rows[i : i + batch])
        for i in range(0, len(sem_rows), batch):
            StudentSemesterAverage.objects.bulk_create(sem_rows[i : i + batch])
        for i in range(0, len(year_rows), batch):
            StudentYearAverage.objects.bulk_create(year_rows[i : i + batch])

    return {
        'student_subject_semester_rows': len(ss_rows),
        'student_semester_rows': len(sem_rows),
        'student_year_rows': len(year_rows),
        'students_warning_not_eleven_subjects': warnings_not_eleven,
    }
