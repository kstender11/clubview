const LOCAL_IP = "http://192.168.1.179:8000"; // ✅ Use your Mac's local IP

export async function fetchVenues(city = "Los Angeles") {
  const res = await fetch(`${LOCAL_IP}/api/venues/discover?city=${encodeURIComponent(city)}`);
  if (!res.ok) throw new Error("Failed to fetch venues");
  return res.json();
}
