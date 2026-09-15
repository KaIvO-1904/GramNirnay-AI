const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
import { UserProfile, AnalysisResult, QuestionnaireResponse, Place, LocationIdentity, VoiceTranscription, AuthResponse } from '@/types';

export async function searchLocation(query: string): Promise<Place[]> {
  const response = await fetch(`${API_BASE_URL}/api/location/search?query=${encodeURIComponent(query)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!response.ok) throw new Error(`Search failed: ${response.status}`);
  return response.json();
}

export async function resolveLocation(providerId: string, source: string): Promise<LocationIdentity> {
  const response = await fetch(`${API_BASE_URL}/api/location/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider_id: providerId, source: source }),
  });
  if (!response.ok) throw new Error(`Resolve failed: ${response.status}`);
  return response.json();
}

export async function resolveGps(lat: number, lng: number): Promise<LocationIdentity> {
  const response = await fetch(`${API_BASE_URL}/api/location/gps`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lat, lng }),
  });
  if (!response.ok) throw new Error(`GPS resolve failed: ${response.status}`);
  return response.json();
}

export async function generateQuestions(businessIdea: string, location: { district: string; state: string }): Promise<QuestionnaireResponse> {

  const response = await fetch(`${API_BASE_URL}/api/generate-questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ businessIdea, location }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `Server error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export async function analyzeViability(profile: UserProfile): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/api/analyze-viability`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `Server error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export async function getDemoScenario(scenarioId: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/api/demo/${scenarioId}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `Server error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export async function uploadVoice(audioBlob: Blob, languageHint?: string): Promise<VoiceTranscription> {
  const formData = new FormData();
  formData.append('audio', audioBlob);

  const url = new URL(`${API_BASE_URL}/api/voice/upload`);
  if (languageHint) url.searchParams.append('language_hint', languageHint);

  const response = await fetch(url.toString(), {
    method: 'POST',
    body: audioBlob, // The backend expects raw bytes in the body
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `Server error: ${response.status}`);
  }
  return response.json();
}

export async function confirmVoice(confirmedText: string): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/api/voice/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ confirmed_text: confirmedText }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `Server error: ${response.status}`);
  }
  return response.json();
}

export interface GoogleAuthPayload {
  credential?: string;
  email?: string;
  name?: string;
  avatar?: string;
  google_id?: string;
}

export async function authenticateWithGoogleBackend(authData: GoogleAuthPayload): Promise<AuthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(authData),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Authentication failed');
    }
    return await response.json();
  } catch (e: any) {
    console.error("Authentication failed:", e.message);
    throw e;
  }
}

export async function fetchUserAnalysesBackend(userId: string): Promise<AnalysisResult[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/user/analyses?user_id=${userId}`);
    if (response.ok) {
      return await response.json();
    }
  } catch (e) {
    console.warn("Could not fetch remote user analyses:", e);
  }
  return [];
}

export async function saveUserAnalysisBackend(userId: string, analysis: AnalysisResult): Promise<AnalysisResult | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/user/analyses?user_id=${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(analysis),
    });
    if (response.ok) {
      return await response.json();
    }
  } catch (e) {
    console.warn("Could not sync analysis to backend:", e);
  }
  return null;
}
