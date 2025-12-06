import { Card, CardContent } from "../ui/card";
import { Hotel as HotelIcon } from "lucide-react";
import { Hotel } from "../../types/trip";

interface HotelCardProps {
    hotel: Hotel;
}

export function HotelCard({ hotel }: HotelCardProps) {
    return (
        <Card className="shadow-sm">
            <CardContent className="p-4">
                <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                        <HotelIcon className="w-5 h-5 text-purple-600" />
                    </div>
                    <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{hotel.nome}</p>
                        <p className="text-xs text-gray-500">{hotel.cidade}</p>
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs">
                    <div>
                        <p className="text-gray-500">Check-in</p>
                        <p className="font-medium text-gray-900">{hotel.checkin}</p>
                    </div>
                    <div>
                        <p className="text-gray-500">Check-out</p>
                        <p className="font-medium text-gray-900">{hotel.checkout}</p>
                    </div>
                    <div>
                        <p className="text-gray-500">Noites</p>
                        <p className="font-medium text-gray-900">{hotel.noites}</p>
                    </div>
                    <div>
                        <p className="text-gray-500">Regime</p>
                        <p className="font-medium text-gray-900">{hotel.regime}</p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}