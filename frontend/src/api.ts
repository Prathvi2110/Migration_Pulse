export type Evidence = { id?: number; title: string; summary: string; region: string; source_name: string; source_url: string; publication_date?: string | null; signal_category: string; evidence_direction: 'positive' | 'negative' | 'neutral'; relevance: number; confidence: number; duplicate_identifier?: string | null };
export type CategoryScore = { label: string; score: number | null; available: boolean; evidence_count: number; weight: number };
export type Analysis = { id: number; region: string; period_days: number; created_at: string; status: string; mode: 'live' | 'demo'; pulse_score: number | null; data_coverage: number; category_scores: Record<string, CategoryScore>; explanation: string; evidence_count: number; evidence: Evidence[] };
export type SimulationInput = { additional_population: number; average_household_size: number; litres_per_person_per_day: number; school_age_percentage: number; students_per_classroom: number; hospital_beds_per_1000: number };
export type Simulation = { inputs: SimulationInput; households_required: number; daily_water_litres: number; classrooms_required: number; hospital_beds_required: number; disclaimer: string };
export type Health = { status: string; database: string; tinyfish_configured: boolean; demo_mode: boolean; timestamp: string };

const base = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base}${path}`, { headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) }, ...init });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed with ${response.status}`);
  }
  return response.json();
}
export const api = {
  health: () => request<Health>('/api/health'),
  analyze: (payload: { region: string; period_days: number }) => request<Analysis>('/api/analyze', { method: 'POST', body: JSON.stringify(payload) }),
  history: () => request<Analysis[]>('/api/analysis-history'),
  analysis: (id: number) => request<Analysis>(`/api/analysis/${id}`),
  evidence: (id: number) => request<Evidence[]>(`/api/evidence/${id}`),
  simulate: (payload: SimulationInput) => request<Simulation>('/api/simulate', { method: 'POST', body: JSON.stringify(payload) }),
};
