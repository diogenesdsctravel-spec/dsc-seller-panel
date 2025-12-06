import { Card, CardContent } from "../ui/card";
import { Plane } from "lucide-react";
import { Flight } from "../../types/trip";

interface FlightCardProps {
    flight: Flight;
}

export function FlightCard({ flight }: FlightCardProps) {
    return (
        <Card className="shadow-sm">
            <CardContent className="p-4">
                <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                        <Plane className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                            {flight.origem} → {flight.destino}
                        </p>
                        <p className="text-xs text-gray-500">{flight.data}</p>
                    </div>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-600">
                    <div>
                        <p className="text-gray-500">Saída</p>
                        <p className="font-medium text-gray-900">{flight.horario_saida}</p>
                    </div>
                    <div className="text-gray-400">→</div>
                    <div>
                        <p className="text-gray-500">Chegada</p>
                        <p className="font-medium text-gray-900">{flight.horario_chegada}</p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}