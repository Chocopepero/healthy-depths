import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60000,
});

export async function sendMessage(history, message) {
  const { data } = await api.post("/api/chat", { history, message });
  return data;
}

export async function checkInteractions(medications) {
  const { data } = await api.post("/api/interactions", { medications });
  return data;
}

export async function getClinics(zip, radius = 10) {
  const { data } = await api.get("/api/clinics", { params: { zip, radius } });
  return data;
}
