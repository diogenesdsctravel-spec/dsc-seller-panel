interface TripHeaderProps {
  tripId: string;
  clientName: string;
}

export function TripHeader({ tripId, clientName }: TripHeaderProps) {
  return (
    <header className="mb-6">
      <h1 className="text-2xl font-normal tracking-tight m-0">
        DSC Travel · Painel do Vendedor
      </h1>
      <p className="mt-1.5 text-gray-500 text-sm">
        Viagem demo carregada da API · id: {tripId}
      </p>
      <p className="mt-0.5 text-gray-600 text-[15px]">
        Cliente: <span className="font-semibold">{clientName}</span>
      </p>
    </header>
  );
}
