import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { TripData } from '../types/trip';

interface RawDataPanelProps {
  data: TripData;
}

export function RawDataPanel({ data }: RawDataPanelProps) {
  return (
    <Card className="shadow-[0_18px_45px_rgba(15,23,42,0.08)]">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-normal">Dados crus da extração</CardTitle>
      </CardHeader>
      <CardContent>
        <pre className="bg-gray-50 rounded-[14px] p-3 text-[11px] leading-normal overflow-auto max-h-[420px]">
          {JSON.stringify(data, null, 2)}
        </pre>
      </CardContent>
    </Card>
  );
}