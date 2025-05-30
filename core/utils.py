import logging
from .models import Attendance, Staff, Student, Device, SchoolAdmin
from django.utils.timezone import make_aware
import datetime
from fcm.send_fcm import send_fcm_notification

logger = logging.getLogger('core')  # Make sure your logging config uses this name


def process_attendance_data(post_data, device_sn):
    logger.info(f"🚀 Called process_attendance_data with device_sn={device_sn} and post_data:\n{post_data}")

    device = Device.objects.filter(serial_number=device_sn).first()
    if not device:
        logger.warning(f"Device with SN {device_sn} not found.")
        return

    lines = post_data.strip().split('\n')

    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) < 2:
            logger.warning(f"Skipping invalid line: {line}")
            continue

        user_id = parts[0]
        timestamp_str = parts[1]
        status = parts[2] if len(parts) > 2 else '0'
        logger.info(f"Parsing line: user_id={user_id}, timestamp={timestamp_str}, status={status}")

        try:
            user_obj = None
            user_type = None
            try:
                user_obj = Staff.objects.get(user__id=user_id)
                user_type = 'staff'
                logger.info(f"Found staff user_obj: {user_obj}")
            except Staff.DoesNotExist:
                try:
                    user_obj = Student.objects.get(user__id=user_id)
                    user_type = 'student'
                    logger.info(f"Found student user_obj: {user_obj}")
                except Student.DoesNotExist:
                    logger.warning(f"User with ID {user_id} not found in staff or student.")
                    continue

            raw_dt = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            arrival_time = make_aware(raw_dt.replace(microsecond=0))

            existing = Attendance.objects.filter(
                staff=user_obj if user_type == 'staff' else None,
                student=user_obj if user_type == 'student' else None,
                arrival_time=arrival_time
            ).first()

            if existing:
                logger.info(f"⏩ Duplicate entry for {user_type} ID {user_obj.id} at {arrival_time}")
                if status == '1':
                    existing.departure_time = arrival_time
                    existing.save()
                    logger.info(f"✅ Updated departure time for {user_type} ID {user_obj.id}")
            else:
                att = Attendance.objects.create(
                    attendee_type=user_type,
                    staff=user_obj if user_type == 'staff' else None,
                    student=user_obj if user_type == 'student' else None,
                    arrival_time=arrival_time,
                    device=device,
                    department=user_obj.department if user_type == 'staff' else None,
                    school=user_obj.school,
                    student_class=user_obj.student_class if user_type == 'student' else None
                )
                logger.info(f"✅ Attendance created for {user_type} ID {user_obj.id} at {arrival_time}")

                # Log FCM token for this user, even if it's None or empty
                fcm_token = getattr(user_obj, 'fcm_token', None)
                if fcm_token:
                    logger.info(f"📱 FCM Token for user {user_obj.user.username}: {fcm_token}")
                else:
                    logger.info(f"📱 No FCM Token found for user {user_obj.user.username} (fcm_token is None or empty)")

                # Send FCM notification to user
                if fcm_token:
                    message = f"{user_obj.user.get_full_name()} checked in at {arrival_time.strftime('%H:%M:%S')}"
                    send_fcm_notification(
                        token=fcm_token,
                        title="🕒 Attendance Logged",
                        body=message
                    )

                # Notify school admins with FCM
                school_admins = SchoolAdmin.objects.filter(school=user_obj.school)
                for admin in school_admins:
                    admin_token = getattr(admin, 'fcm_token', None)
                    if admin_token:
                        admin_message = f"{user_type.title()} {user_obj.user.get_full_name()} checked in at {arrival_time.strftime('%H:%M:%S')}"
                        send_fcm_notification(
                            token=admin_token,
                            title="📢 Attendance Alert",
                            body=admin_message
                        )
                    else:
                        logger.info(f"📱 No FCM Token for school admin {admin.user.username}")

        except Exception as e:
            logger.exception(f"❌ Unexpected error while processing attendance for user ID {user_id}: {e}")
