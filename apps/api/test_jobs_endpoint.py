import sys
sys.path.insert(0, '/Users/brahmatejakanchibhotla/Documents/projects/aijobapplyportal/apps/api')

from database import SessionLocal
from routers.job import get_jobs

try:
    db = SessionLocal()
    result = get_jobs(skip=0, limit=10, db=db)
    print(f"Success! Retrieved {len(result)} jobs")
    for job in result[:3]:
        print(f"- {job.title}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
