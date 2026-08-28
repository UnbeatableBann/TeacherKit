import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { OrchestratorResponse, LeadItem } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useLeads(tenantId?: string) {
  return useQuery<LeadItem[]>({
    queryKey: ['leads', tenantId],
    queryFn: async () => {
      // Return dummy data if API is not running, so UI shows something
      try {
        const url = new URL(`${API_URL}/leads`);
        if (tenantId) url.searchParams.append('tenant_id', tenantId);
        const res = await fetch(url.toString());
        if (!res.ok) throw new Error('Network response was not ok');
        return res.json();
      } catch (err) {
        console.warn("Failed to fetch leads, returning dummy data");
        return [
          { conversation_id: "1", customer_name: "Alice Smith", score: 85, last_activity: new Date().toISOString() },
          { conversation_id: "2", customer_name: "Bob Jones", score: 40, last_activity: new Date(Date.now() - 3600000).toISOString() }
        ];
      }
    }
  });
}

export function useConversation(id: string) {
  return useQuery({
    queryKey: ['conversation', id],
    queryFn: async () => {
      try {
        const res = await fetch(`${API_URL}/conversations/${id}`);
        if (!res.ok) throw new Error('Network response was not ok');
        return res.json();
      } catch (err) {
        console.warn("Failed to fetch conversation state");
        return {
          id,
          requirements: { features_wanted: [], preferences: [] },
          lead_score: { total: 0, breakdown: {} },
          recommendations_shown: []
        };
      }
    }
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, message }: { id: string; message: string }) => {
      const res = await fetch(`${API_URL}/conversations/${id}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_message: message })
      });
      if (!res.ok) throw new Error('Failed to send message');
      return res.json() as Promise<OrchestratorResponse>;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['conversation', variables.id] });
    }
  });
}

export function useGenerateFollowUp() {
  return useMutation({
    mutationFn: async (conversationId: string) => {
      const res = await fetch(`${API_URL}/conversations/${conversationId}/follow-up`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to generate follow-up');
      return res.json();
    }
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ customer_name }: { customer_name: string }) => {
      const res = await fetch(`${API_URL}/conversations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_name })
      });
      if (!res.ok) throw new Error('Failed to create conversation');
      return res.json() as Promise<{ conversation_id: string }>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    }
  });
}
