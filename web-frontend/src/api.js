export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "/api";
export const BACKEND_LABEL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function parseResponse(response) {
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(`Backend returned a non-JSON response (${response.status}).`);
  }

  if (!response.ok) {
    const detail = data?.detail;
    throw new Error(
      typeof detail === "string"
        ? detail
        : `Backend request failed (${response.status}).`,
    );
  }
  return data;
}

export async function apiGet(path, params = {}) {
  const url = new URL(`${API_BASE_URL}${path}`, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined && value !== "Any") {
      url.searchParams.set(key, value);
    }
  });
  return parseResponse(
    await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
    }),
  );
}

export function getDealerLeads(params = {}) {
  return apiGet("/dealer/leads", params);
}

export function getDealerships() {
  return apiGet("/dealer/dealerships");
}

export function dealerLogin(email, password) {
  return apiPost("/dealer/auth/login", { email, password });
}

async function dealerAuthGet(path, token, params = {}) {
  const url = new URL(`${API_BASE_URL}${path}`, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      url.searchParams.set(key, value);
    }
  });
  return parseResponse(
    await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    }),
  );
}

export function getDealerProfile(token) {
  return dealerAuthGet("/dealer/auth/me", token);
}

export function getMyDealerLeads(token, params = {}) {
  return dealerAuthGet("/dealer/me/leads", token, params);
}

export async function apiPost(path, payload) {
  return parseResponse(
    await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
}

export async function compareCars(carIds) {
  const response = await fetch(`${API_BASE_URL}/compare/cars`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ car_ids: carIds }),
  });

  if (response.status === 404) {
    return apiPost("/compare", { car_ids: carIds });
  }

  return parseResponse(response);
}

export async function uploadImage(file) {
  const formData = new FormData();
  formData.append("file", file);
  return parseResponse(
    await fetch(`${API_BASE_URL}/image/analyze`, {
      method: "POST",
      body: formData,
    }),
  );
}
