import { API_BASE_URL } from "../config";

const isTokenExpired = (token) => {
  if (!token) return true;

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (error) {
    return true;
  }
};

export const apiRequest = async (url, options = {}) => {
  const token = localStorage.getItem("access_token");

  if (token && isTokenExpired(token)) {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
    throw new Error("Token expired");
  }

  const defaultOptions = {
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${url}`, defaultOptions);

    if (response.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }

    return response;
  } catch (error) {
    console.error("API request error:", error);
    throw error;
  }
};

export const apiGet = (url) => apiRequest(url);

export const apiPost = (url, data) =>
  apiRequest(url, {
    method: "POST",
    body: JSON.stringify(data),
  });

export const apiPut = (url, data) =>
  apiRequest(url, {
    method: "PUT",
    body: JSON.stringify(data),
  });

export const apiDelete = (url) =>
  apiRequest(url, {
    method: "DELETE",
  });

export const validateToken = async () => {
  try {
    await apiGet("/roles");
    return true;
  } catch (error) {
    return false;
  }
};
