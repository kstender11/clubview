import { API_BASE_URL } from '@env'; // ✅ This pulls from .env

export async function fetchVenues(city = "Los Angeles") {
  const res = await fetch(`${API_BASE_URL}/api/venues/discover?city=${encodeURIComponent(city)}`);
  if (!res.ok) throw new Error("Failed to fetch venues");
  return res.json();
}
