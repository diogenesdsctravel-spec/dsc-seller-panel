import { useTrip } from "./hooks/useTrip";
import { getClientName, getTripSummary } from "./utils/formatters";
import { LoadingState } from "./components/LoadingState";
import { ErrorState } from "./components/ErrorState";
import { EmptyState } from "./components/EmptyState";
import { TripHeader } from "./components/TripHeader";
import { TripSummary } from "./components/TripSummary";
import { BudgetSection } from "./components/BudgetSection";
import { ProductsSection } from "./components/ProductsSection";
import { RawDataPanel } from "./components/RawDataPanel";

function App() {
  const { trip, loading, error } = useTrip("demo");

  if (loading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;
  if (!trip) return <EmptyState />;

  const data = trip.data || {};
  const clientName = getClientName(data);
  const resumo = getTripSummary(data);

  return (
    <div className="min-h-screen bg-gray-100 p-6 font-sans">
      <TripHeader tripId={trip.trip_id} clientName={clientName} />

      <main className="grid grid-cols-[1fr_1fr_400px] gap-6">
        <div className="space-y-6">
          <TripSummary resumo={resumo} />
          <BudgetSection data={data} />
        </div>
        <ProductsSection data={data} />
        <RawDataPanel data={data} />
      </main>
    </div>
  );
}

export default App;