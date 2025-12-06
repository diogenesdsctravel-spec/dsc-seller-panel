import { Card, CardContent } from "../ui/card";
import { Compass } from "lucide-react";
import { Tour } from "../../types/trip";

interface TourCardProps {
    tour: Tour;
}

export function TourCard({ tour }: TourCardProps) {
    return (
        <Card className="shadow-sm">
            <CardContent className="p-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                        <Compass className="w-5 h-5 text-green-600" />
                    </div>
                    <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{tour.nome}</p>
                        <div className="flex items-center gap-2 mt-1">
                            <p className="text-xs font-medium text-green-600">
                                R$ {tour.valor_por_pessoa.toFixed(2)}
                            </p>
                            <span className="text-xs text-gray-400">•</span>
                            <p className="text-xs text-gray-500">por pessoa</p>
                        </div>
                    </div>
                    {tour.incluido && (
                        <div className="px-2 py-1 bg-green-50 rounded text-xs font-medium text-green-700">
                            Incluso
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}