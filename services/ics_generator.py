import os

def create_ics_file(event: dict) -> str:
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{event['summary']}
DTSTART:{event['dtstart']}
DTEND:{event['dtend']}
LOCATION:{event['location']}
DESCRIPTION:{event['description']}
END:VEVENT
END:VCALENDAR
"""
    file_path = os.path.join(os.getcwd(), f"{event['summary'].replace(' ', '_')}.ics")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(ics_content)
    return file_path
