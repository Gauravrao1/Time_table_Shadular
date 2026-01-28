from typing import List, Optional

from .models import Course, Room, Assignment

DEFAULT_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
DEFAULT_SLOTS = [
    "09:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
    "12:00-13:00",
    "13:00-14:00",
    "14:00-15:00",
    "15:00-16:00",
]


def generate_schedule(db, days: Optional[List[str]] = None, slots: Optional[List[str]] = None) -> List[Assignment]:
    courses = db.query(Course).all()
    rooms = db.query(Room).order_by(Room.capacity.asc()).all()

    assignments: List[Assignment] = []

    # Track occupancy
    teacher_busy = set()
    section_busy = set()
    room_busy = set()

    days = days or DEFAULT_DAYS
    slots = slots or DEFAULT_SLOTS

    for course in courses:
        placed = False
        for day in days:
            if placed:
                break
            for slot in slots:
                if placed:
                    break
                t_key = (course.teacher_id, day, slot)
                s_key = (course.section_id, day, slot)
                if t_key in teacher_busy or s_key in section_busy:
                    continue
                # choose the smallest room that fits
                for room in rooms:
                    r_key = (room.id, day, slot)
                    if r_key in room_busy:
                        continue
                    if room.capacity < course.section.size:
                        continue
                    # assign
                    a = Assignment(
                        course_id=course.id,
                        teacher_id=course.teacher_id,
                        section_id=course.section_id,
                        room_id=room.id,
                        day=day,
                        slot=slot,
                    )
                    assignments.append(a)
                    teacher_busy.add(t_key)
                    section_busy.add(s_key)
                    room_busy.add(r_key)
                    placed = True
                    break
        if not placed:
            # course could not be placed
            pass

    return assignments
