import { useState, useCallback } from "react";
import { sendMessage } from "../api/client";

export function useChat() {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stage, setStage] = useState("INTAKE");
  const [clinicalSummary, setClinicalSummary] = useState(null);
  const [triage, setTriage] = useState(null);
  const [drugInteractions, setDrugInteractions] = useState(null);
  const [clinics, setClinics] = useState(null);

  const send = useCallback(
    async (userMessage) => {
      if (!userMessage.trim() || isLoading) return;

      const newUserMsg = { role: "user", content: userMessage };
      const optimisticHistory = [...history, newUserMsg];
      setHistory(optimisticHistory);
      setIsLoading(true);
      setError(null);

      try {
        const response = await sendMessage(
          history.map((m) => ({ role: m.role, content: m.content })),
          userMessage
        );

        const assistantMsg = { role: "model", content: response.message };
        setHistory([...optimisticHistory, assistantMsg]);
        setStage(response.stage);

        if (response.clinical_summary) setClinicalSummary(response.clinical_summary);
        if (response.triage) setTriage(response.triage);
        if (response.drug_interactions) setDrugInteractions(response.drug_interactions);
        if (response.clinics) setClinics(response.clinics);
      } catch (err) {
        setError("Something went wrong. Please try again.");
        setHistory(history);
      } finally {
        setIsLoading(false);
      }
    },
    [history, isLoading]
  );

  const reset = useCallback(() => {
    setHistory([]);
    setStage("INTAKE");
    setClinicalSummary(null);
    setTriage(null);
    setDrugInteractions(null);
    setClinics(null);
    setError(null);
  }, []);

  return {
    history,
    isLoading,
    error,
    stage,
    clinicalSummary,
    triage,
    drugInteractions,
    clinics,
    send,
    reset,
  };
}
