/**
 * API Client Utility for communicating with the FastAPI backend
 */

const API_BASE = '/api';

export const apiClient = {
  async getHistory() {
    const res = await fetch(`${API_BASE}/history`);
    if (!res.ok) throw new Error('Failed to fetch history');
    return res.json();
  },

  async deleteHistoryEntry(id) {
    const res = await fetch(`${API_BASE}/history/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete history entry');
    return res.json();
  },

  async clearHistory() {
    const res = await fetch(`${API_BASE}/history`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to clear history');
    return res.json();
  }
};
