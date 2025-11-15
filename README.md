## Event & Slot Booking Platform

RESTful Django backend that lets users browse venues/events/slots, book or cancel time slots, and gives admins fine-grained controls via Django Admin. The project also ships with JWT authentication, automated booking validations, Swagger UI, Postman collection, ER diagram, and regression tests for booking rules.

### Tech Stack
- Python 3 / Django 5 / Django REST Framework
- MySQL (change `DATABASES` in `eventslotbooking_project/settings.py` for other engines)
- JWT auth via `djangorestframework-simplejwt`
- drf-yasg for Swagger docs

### Getting Started
1. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure database**
   - Update `DATABASES` in `eventslotbooking_project/settings.py`
   - Create the DB manually (e.g. `CREATE DATABASE slot_booking;`)
3. **Run migrations & seed roles (optional)**
   ```bash
   python manage.py migrate
   ```
4. **Create a superuser for Django Admin**
   ```bash
   python manage.py createsuperuser
   ```
5. **Run the server**
   ```bash
   python manage.py runserver
   ```

### API Overview
All endpoints live under `/api/` and are documented in Swagger (`/swagger/`) and the included Postman collection (`docs/postman_collection.json`).

| Module | Endpoint | Methods | Notes |
| --- | --- | --- | --- |
| Auth | `/api/auth/register/` | POST | Public |
| Auth | `/api/auth/login/` | POST | Public, returns JWT |
| Venues | `/api/venues/` | GET, POST | GET is public; POST requires auth |
| Venues | `/api/venues/{id}/` | GET, PATCH, DELETE | Soft delete |
| Events | `/api/events/` | GET, POST | Filtering by search/start/end date |
| Events | `/api/events/{id}/` | GET, PATCH, DELETE | |
| Slots | `/api/slots/` | GET, POST | Filter by event/date/block state |
| Slots | `/api/slots/{id}/` | GET, PATCH, DELETE | |
| Bookings | `/api/bookings/` | GET, POST | Auth required; GET auto-scopes to current user |
| Bookings | `/api/bookings/{id}/` | GET, PATCH | Users can only access their bookings |
| Bookings | `/api/bookings/{id}/cancel/` | POST | Marks booking as `CANCELLED` |

### Booking Business Rules
- Blocked or deleted slots cannot be booked.
- Slot capacity can’t be exceeded; approvals re-check capacity in real time.
- Users cannot hold overlapping bookings (pending or approved) for the same time window.
- Cancelling frees capacity immediately.
- Serializer + model validations prevent tampering (e.g. forcing booked status without admin rights).

### Admin Portal Highlights
- Venue/Event CRUD with slot inline editing for events.
- Slot admin actions to block/unblock or soft delete, with date filters.
- Booking admin actions for approve/cancel/export attendees CSV, with validation feedback.
- Permissions respect `RolePermission` helper so modules can be hidden per role.

### Documentation Deliverables
- `README.md` (this file)
- Swagger/OpenAPI via `/swagger/` and `/redoc/`
- `docs/postman_collection.json` covering Auth/Venues/Events/Slots/Bookings flows
- `docs/ERD.md` with a Mermaid ER diagram
- Automated booking unit tests in `bookings/tests.py`

### Running Tests
```bash
python manage.py test bookings
```

### Next Steps / Optional Enhancements
- Email notifications on booking status change
- Analytics endpoints for occupancy trends
- Background jobs for reminders

