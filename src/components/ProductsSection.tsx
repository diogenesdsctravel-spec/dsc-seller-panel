import { TripData } from "../types/trip";
import { FlightCard } from "./products/FlightCard";
import { HotelCard } from "./products/HotelCard";
import { TourCard } from "./products/TourCard";

interface ProductsSectionProps {
    data: TripData;
}

export function ProductsSection({ data }: ProductsSectionProps) {
    const hasProducts =
        (data.voos && data.voos.length > 0) ||
        (data.hoteis && data.hoteis.length > 0) ||
        (data.passeios && data.passeios.length > 0);

    if (!hasProducts) {
        return null;
    }

    return (
        <div className="space-y-6">
            {/* Voos */}
            {data.voos && data.voos.length > 0 && (
                <div>
                    <h2 className="text-lg font-semibold mb-3 text-gray-900">Voos</h2>
                    <div className="space-y-3">
                        {data.voos.map((voo, index) => (
                            <FlightCard key={index} flight={voo} />
                        ))}
                    </div>
                </div>
            )}

            {/* Hotéis */}
            {data.hoteis && data.hoteis.length > 0 && (
                <div>
                    <h2 className="text-lg font-semibold mb-3 text-gray-900">Hotéis</h2>
                    <div className="space-y-3">
                        {data.hoteis.map((hotel, index) => (
                            <HotelCard key={index} hotel={hotel} />
                        ))}
                    </div>
                </div>
            )}

            {/* Passeios */}
            {data.passeios && data.passeios.length > 0 && (
                <div>
                    <h2 className="text-lg font-semibold mb-3 text-gray-900">Passeios</h2>
                    <div className="space-y-3">
                        {data.passeios.map((passeio, index) => (
                            <TourCard key={index} tour={passeio} />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}