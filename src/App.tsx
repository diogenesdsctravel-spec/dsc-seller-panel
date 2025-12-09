import { useState } from "react";
import { useTrip } from "./hooks/useTrip";
import { getClientName, getTripSummary } from "./utils/formatters";
import { LoadingState } from "./components/LoadingState";
import { ErrorState } from "./components/ErrorState";
import { EmptyState } from "./components/EmptyState";
import { TripHeader } from "./components/TripHeader";
import { TripSummary } from "./components/TripSummary";
import { BudgetSection } from "./components/BudgetSection";
import { ProductsSection } from "./components/ProductsSection";
import { UploadSection } from "./components/UploadSection";
import { AppPreview } from "./components/AppPreview";

function App() {
  const [currentTripId, setCurrentTripId] = useState<string>("demo");
  const { trip, loading, error, refetch } = useTrip(currentTripId);

  const handleUploadSuccess = (tripId: string) => {
    console.log("Upload sucesso! Trip ID:", tripId);
    setCurrentTripId(tripId);
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;
  if (!trip) return <EmptyState />;

  const data = trip.data || {};
  const clientName = getClientName(data);
  const resumo = getTripSummary(data);

  return (
    <div key={currentTripId} className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-[1600px] mx-auto px-6 py-6">
          <TripHeader tripId={trip.trip_id} clientName={clientName} />
        </div>
      </div>

      {/* 3 Colunas */}
      <main className="max-w-[1600px] mx-auto px-6 py-8">
        <div className="grid grid-cols-[340px_1fr_420px] gap-6">

          {/* COLUNA 1 - Upload */}
          <div>
            <UploadSection onUploadSuccess={handleUploadSuccess} onRefetch={refetch} />
          </div>

          {/* COLUNA 2 - Revisão */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-[#09077D]">
              2. Revise os dados extraídos pela IA
            </h2>
            <TripSummary resumo={resumo} />
            <ProductsSection data={data} />
            <BudgetSection data={data} />
          </div>

          {/* COLUNA 3 - Preview */}
          <div>
            <AppPreview tripData={data} />
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
