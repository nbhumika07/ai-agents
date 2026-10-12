from __future__ import annotations

from datetime import date
from typing import Callable, Any
from pydantic import BaseModel
from .models import Flight, Hotel


class FlightSearchInput(BaseModel):
    origin: str
    destination: str
    travel_date: date
    max_price: float


class HotelSearchInput(BaseModel):
    location: str
    max_nightly_price: float
    required_amenities: list[str]


# Fictional classroom inventory; never connects to suppliers or takes payment.
FLIGHTS = [
    # Date-flexible route templates for the classroom simulator. The requested date
    # is copied into the result; these are never live schedules.
    Flight(flight_id="IN-BLR-DEL-01", origin="Bengaluru", destination="Delhi", travel_date=date(2026, 11, 10), price=7200, airline="Demo Air"),
    Flight(flight_id="IN-BLR-BOM-01", origin="Bengaluru", destination="Mumbai", travel_date=date(2026, 11, 10), price=6200, airline="Demo Air"),
    Flight(flight_id="IN-BOM-DEL-01", origin="Mumbai", destination="Delhi", travel_date=date(2026, 11, 10), price=5800, airline="Sample Airways"),
    Flight(flight_id="IN-DEL-JAI-01", origin="Delhi", destination="Jaipur", travel_date=date(2026, 11, 10), price=4200, airline="Sample Airways"),
    Flight(flight_id="IN-BLR-MYS-01", origin="Bengaluru", destination="Mysuru", travel_date=date(2026, 11, 10), price=2500, airline="Demo Air"),
    Flight(flight_id="IN-MAA-DEL-01", origin="Chennai", destination="Delhi", travel_date=date(2026, 11, 10), price=7800, airline="Demo Air"),
    Flight(flight_id="FL-101", origin="Boston", destination="London", travel_date=date(2026, 11, 10), price=28000, airline="Northstar Air"),
    Flight(flight_id="FL-102", origin="Boston", destination="London", travel_date=date(2026, 11, 10), price=34000, airline="Atlantic Demo"),
    Flight(flight_id="FL-103", origin="Boston", destination="London", travel_date=date(2026, 11, 11), price=26000, airline="Northstar Air"),
]
HOTELS = [
    Hotel(hotel_id="HT-MYS-01", location="Mysuru", name="Mysuru Heritage Stay", nightly_price=2400, amenities=["wifi", "breakfast"]),
    Hotel(hotel_id="HT-MYS-02", location="Mysuru", name="Garden View Lodge", nightly_price=1800, amenities=["wifi"]),
    Hotel(hotel_id="HT-BLR-01", location="Bengaluru", name="Bengaluru City Hotel", nightly_price=3900, amenities=["wifi", "breakfast"]),
    Hotel(hotel_id="HT-DEL-01", location="Delhi", name="Capital Comfort Inn", nightly_price=4200, amenities=["wifi", "breakfast", "accessible"]),
    Hotel(hotel_id="HT-BOM-01", location="Mumbai", name="Harbour View Hotel", nightly_price=5200, amenities=["wifi", "breakfast"]),
    Hotel(hotel_id="HT-JAI-01", location="Jaipur", name="Pink City Guest House", nightly_price=2800, amenities=["wifi", "breakfast"]),
    Hotel(hotel_id="HT-MAA-01", location="Chennai", name="Marina Garden Hotel", nightly_price=3500, amenities=["wifi", "breakfast"]),
    Hotel(hotel_id="HT-201", location="London", name="City Garden Hotel", nightly_price=15500, amenities=["wifi", "breakfast", "accessible"]),
    Hotel(hotel_id="HT-202", location="London", name="Budget Square Inn", nightly_price=10500, amenities=["wifi"]),
    Hotel(hotel_id="HT-203", location="London", name="Riverside Suites", nightly_price=18500, amenities=["wifi", "breakfast", "pool"]),
]
BOOKINGS: list[dict[str, Any]] = []


def _city_key(city: str) -> str:
    aliases = {"bangalore": "bengaluru", "mysore": "mysuru", "bombay": "mumbai", "new delhi": "delhi"}
    key = " ".join(city.casefold().split())
    return aliases.get(key, key)


def search_flights(origin: str, destination: str, date: date, max_price: float) -> list[Flight]:
    """Search fictional flights.

    Args:
        origin: Departure city.
        destination: Arrival city.
        date: Requested departure date.
        max_price: Maximum acceptable one-way fare in INR.
    Returns:
        Date-flexible fictional flights for the route and price. The requested date
        is attached to each result; this is demonstration inventory, not a schedule.
    """
    request = FlightSearchInput(origin=origin, destination=destination, travel_date=date, max_price=max_price)
    results = []
    for flight in FLIGHTS:
        if (flight.available and _city_key(flight.origin) == _city_key(request.origin)
                and _city_key(flight.destination) == _city_key(request.destination)
                and flight.price <= request.max_price):
            results.append(flight.model_copy(update={"travel_date": request.travel_date}))
    return results


def search_hotels(location: str, max_nightly_price: float, required_amenities: list[str]) -> list[Hotel]:
    """Search fictional hotels by nightly cap and required amenities.

    Args:
        location: City where lodging is required.
        max_nightly_price: Maximum nightly rate in INR.
        required_amenities: Every listed amenity must be offered by a hotel.
    Returns:
        Hotels meeting all filters; empty list means no match.
    """
    request = HotelSearchInput(location=location, max_nightly_price=max_nightly_price, required_amenities=required_amenities)
    amenities = {a.casefold() for a in request.required_amenities}
    return [h for h in HOTELS if h.available and _city_key(h.location) == _city_key(request.location)
            and h.nightly_price <= request.max_nightly_price
            and amenities.issubset({a.casefold() for a in h.amenities})]


def execute_booking_transaction(flight_id: str, hotel_id: str, total_cost: float) -> dict[str, Any]:
    """Execute a simulated booking transaction after the agent approval gate.

    This classroom adapter is idempotent per flight/hotel pair. Replace with a
    supplier's transactional API only behind authentication, idempotency, audit,
    and the same human-approval boundary. It does not charge or reserve anything.
    """
    existing = next((b for b in BOOKINGS if b["flight_id"] == flight_id and b["hotel_id"] == hotel_id), None)
    if existing:
        return existing
    flight = next((f for f in FLIGHTS if f.flight_id == flight_id and f.available), None)
    hotel = next((h for h in HOTELS if h.hotel_id == hotel_id and h.available), None)
    if not flight or not hotel:
        raise RuntimeError("Selected inventory is no longer available; re-run search.")
    if total_cost < 0:
        raise ValueError("Transaction total cannot be negative.")
    receipt = {"status": "simulated_success", "booking_id": f"DEMO-{len(BOOKINGS) + 1:04d}",
               "flight_id": flight_id, "hotel_id": hotel_id, "total_cost": total_cost, "currency": "INR"}
    BOOKINGS.append(receipt)
    return receipt


class ToolRegistry:
    """Explicit allow-list of callable tools; no dynamic eval or arbitrary imports."""
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {
            "search_flights": search_flights,
            "search_hotels": search_hotels,
            "execute_booking_transaction": execute_booking_transaction,
        }

    def get(self, name: str) -> Callable[..., Any]:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ValueError(f"Tool is not registered: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._tools)
