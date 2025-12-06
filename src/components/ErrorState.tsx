interface ErrorStateProps {
  error: string;
}

export function ErrorState({ error }: ErrorStateProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-red-50 font-sans">
      <p className="text-red-700">Erro ao carregar viagem: {error}</p>
    </div>
  );
}
