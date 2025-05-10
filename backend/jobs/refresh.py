from apscheduler.schedulers.background import BackgroundScheduler
from models.venue import Venue
from services import google_places, foursquare

def refresh_stale():
    stale = Venue.select().where(
        Venue.last_verified_at < dt.datetime.utcnow() - dt.timedelta(days=7)
    )
    for ven in stale:
        data = google_places.get_detail(ven.place_id, force_refresh=True)
        ven.update_from_api(data)
        ven.save()

sched = BackgroundScheduler()
sched.add_job(refresh_stale, "cron", hour=4)  # nightly 4 AM
sched.start()
