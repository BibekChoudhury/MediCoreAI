import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const AUTH_TOKEN_KEY = 'medicore_auth_token';
export const AUTH_SESSION_TOKEN_KEY = 'medicore_auth_session_token';

const api = axios.create({ baseURL: API_BASE });

export function getApiBase() {
  return API_BASE;
}

export function getStoredToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY) || sessionStorage.getItem(AUTH_SESSION_TOKEN_KEY);
}

export function storeToken(token, rememberMe = false) {
  clearStoredToken();
  if (rememberMe) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    return;
  }
  sessionStorage.setItem(AUTH_SESSION_TOKEN_KEY, token);
}

export function clearStoredToken() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  sessionStorage.removeItem(AUTH_SESSION_TOKEN_KEY);
}

api.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearStoredToken();
      if (window.location.pathname.startsWith('/dashboard')) {
        window.location.replace('/login');
      }
    }
    return Promise.reject(error);
  },
);

export async function fetchSymptoms() {
  const { data } = await api.get('/api/symptoms');
  return data.symptoms || [];
}

export async function registerUser(payload) {
  const { data } = await api.post('/register', payload);
  return data;
}

export async function loginUser(payload) {
  const { data } = await api.post('/login', payload);
  return data;
}

export async function fetchProfile() {
  const { data } = await api.get('/profile');
  return data;
}

export async function updateProfile(payload) {
  const { data } = await api.put('/profile', payload);
  return data;
}

export async function uploadPrescriptionFiles(files) {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  const { data } = await api.post('/upload-prescriptions', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function logoutUser() {
  const { data } = await api.post('/logout');
  return data;
}

export async function fetchMetadata() {
  const { data } = await api.get('/api/metadata');
  return data;
}

export async function predictDisease(symptoms) {
  const { data } = await api.post('/api/predict', { symptoms });
  return data;
}

export async function fullConsultation(formData) {
  const { data } = await api.post('/api/ai/full-consultation', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function textToSpeech(text, language = 'en') {
  const { data } = await api.post('/api/ai/text-to-speech', { text, language });
  return data;
}

export async function analyzePrescription(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/api/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function analyzeHealthReport(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/api/analyze-health-report', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}
