# use this script if cdata and zkteco api is not working. (MADE BY SANTOSH RAWAL)

# import os
# import django
# import requests
# from django.utils import timezone
# import pytz
# from zk import ZK
#
# # Set up Django environment
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendence.settings")
# django.setup()
#
# from core.models import Staff, Attendance
# from core.utils import process_attendance_data  # Keep both usages
#
# DEVICE_IP = '192.168.18.232'
# DEVICE_PORT = 5000
# DEVICE_SN = 'VGU6243900035'
#
#
# def main():
#     zk = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=5, force_udp=False, encoding='utf-8')
#     try:
#         conn = zk.connect()
#         conn.disable_device()
#
#         logs = conn.get_attendance()
#         print(f"Total logs fetched: {len(logs)}")
#
#         nepal_tz = pytz.timezone('Asia/Kathmandu')
#         today = timezone.localtime(timezone.now(), nepal_tz).date()
#
#         lines = []
#
#         for log in logs:
#             user_id = log.user_id  # ZKTeco user ID
#
#             # Convert and localize timestamp
#             utc_dt = log.timestamp
#             if timezone.is_naive(utc_dt):
#                 utc_dt = timezone.make_aware(utc_dt, timezone=pytz.UTC)
#             nepali_dt = timezone.localtime(utc_dt, nepal_tz)
#
#             # Lookup staff by user_id to get real staff_id, school_id, department_id
#             try:
#                 staff = Staff.objects.get(user__id=user_id)
#             except Staff.DoesNotExist:
#                 print(f"❌ No Staff found with user ID: {user_id}")
#                 continue
#
#             # ✅ DUPLICATE CHECK: Skip if attendance for this timestamp already exists
#             normalized_arrival = nepali_dt.replace(microsecond=0)
#             if Attendance.objects.filter(staff=staff, arrival_time=normalized_arrival).exists():
#                 print(f"⏩ Skipped duplicate log for staff ID {staff.id} at {nepali_dt}")
#                 continue
#
#             staff_id = staff.id
#             school_id = staff.school.id
#             department_id = staff.department.id
#
#             # Prepare API POST data
#             time_str = nepali_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
#             url = f"http://127.0.0.1:8000/api/school/{school_id}/department/{department_id}/staff/{staff_id}/attendance/"
#             payload = {
#                 "serial": DEVICE_SN,
#                 "timestamp": time_str
#             }
#
#             response = requests.post(url, json=payload)
#             if response.status_code in [200, 201]:
#                 print(f"✅ Posted for staff ID {staff_id} (user ID {user_id}) at {time_str}")
#             else:
#                 print(f"❌ Failed to post: {response.status_code} | {response.text}")
#
#             # Only prepare for bulk processing if attendance is from today
#             if nepali_dt.date() != today:
#                 continue
#
#             # Prepare bulk data line for process_attendance_data
#             line = f"{user_id}\t{nepali_dt.strftime('%Y-%m-%d %H:%M:%S')}\t1"
#             lines.append(line)
#
#         # Bulk call to your processing utility function
#         if lines:
#             post_data = "\n".join(lines)
#             process_attendance_data(post_data, DEVICE_SN)
#         else:
#             print("No valid logs to process for today.")
#
#         conn.enable_device()
#         conn.disconnect()
#
#     except Exception as e:
#         print("Error:", e)
#
#
# if __name__ == '__main__':
#     main()
