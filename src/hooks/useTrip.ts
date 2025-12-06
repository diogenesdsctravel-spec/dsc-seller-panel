import { useEffect, useState } from "react";
import { getTrip } from "../services/tripService";
import { Trip } from "../types/trip";

export function useTrip(tripId: string) {
  const [trip, setTrip] = useState<Trip | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchTrip() {
      setLoading(true);
      setError(null);

      try {
        const data = await getTrip(tripId);
        if (!cancelled) {
          setTrip(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Erro ao carregar viagem");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchTrip();

    return () => {
      cancelled = true;
    };
  }, [tripId]);

  return { trip, loading, error };
}
