import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface TripSummaryProps {
  resumo: string;
}

export function TripSummary({ resumo }: TripSummaryProps) {
  return (
    <Card className="shadow-[0_18px_45px_rgba(15,23,42,0.08)]">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-normal">Resumo da viagem</CardTitle>
      </CardHeader>
      <CardContent>
        {resumo ? (
          <p className="text-sm text-gray-700 leading-relaxed">
            {resumo}
          </p>
        ) : (
          <p className="text-sm text-gray-400 leading-relaxed">
            Ainda não há um resumo estruturado. Usaremos os dados crus da
            extração.
          </p>
        )}
      </CardContent>
    </Card>
  );
}