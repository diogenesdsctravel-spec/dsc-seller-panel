import { motion } from 'framer-motion';
import { MapPin } from 'lucide-react';

interface CityInfo {
  name: string;
  description: string;
  imageUrl?: string;
  detailText?: string;
}

interface CidadesIncluidasProps {
  cities: CityInfo[];
  onBack: () => void;
  onVerRoteiro: () => void;
}

export function CidadesIncluidas({ cities, onBack, onVerRoteiro }: CidadesIncluidasProps) {
  const cityDetails: Record<string, string> = {
    "Lima": "Centro histórico, Miraflores, Barranco e a costa mais linda da América do Sul.",
    "Cusco": "Ruínas incas, Vale Sagrado e a porta de entrada para Machu Picchu.",
    "Machu Picchu": "A cidadela perdida dos Incas, entre montanhas e nuvens.",
    "Santiago": "Modernidade, vinícolas e a imponente Cordilheira dos Andes.",
    "Buenos Aires": "Tango, gastronomia e arquitetura europeia na América do Sul.",
  };

  return (
    <div className="px-6 pt-16 pb-[120px]">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <button
          onClick={onBack}
          className="text-[15px] mb-6"
          style={{ color: '#09077D' }}
        >
          ← Voltar
        </button>

        <h1
          className="text-[32px] mb-3 leading-[1.1]"
          style={{ color: '#09077D', letterSpacing: '-0.02em' }}
        >
          Cidades Incluídas
        </h1>
        <p className="text-[16px] leading-[1.5] text-gray-700 mb-10">
          {cities.length === 1
            ? 'Explore este destino único'
            : `Explore ${cities.length === 2
              ? 'dois'
              : cities.length === 3
                ? 'três'
                : cities.length
            } destinos únicos`}
        </p>

        <div className="space-y-5">
          {cities.map((city, index) => (
            <motion.div
              key={city.name}
              className="bg-white rounded-[20px] p-6 shadow-[0_8px_20px_rgba(0,0,0,0.06)]"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
            >
              <div className="flex items-start gap-4 mb-4">
                <div
                  className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0"
                  style={{ background: '#50CFAD' }}
                >
                  <MapPin className="w-7 h-7 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-[20px] mb-1" style={{ color: '#09077D' }}>
                    {city.name}
                  </h3>
                  <p className="text-[14px]" style={{ color: '#6B7280' }}>
                    {city.description}
                  </p>
                </div>
              </div>

              {city.imageUrl && (
                <div
                  className="rounded-[16px] overflow-hidden mb-4"
                  style={{
                    height: cities.length === 1 ? '240px' : '180px',
                  }}
                >
                  <img
                    src={city.imageUrl}
                    alt={city.name}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}

              <p className="text-[15px] leading-[1.5] text-gray-700">
                {cityDetails[city.name] || 'Um destino incrível da sua viagem.'}
              </p>
            </motion.div>
          ))}
        </div>

        <button
          onClick={onVerRoteiro}
          className="w-full mt-8 px-8 py-5 text-white rounded-[16px] text-[17px] transition-all"
          style={{ background: '#09077D', boxShadow: '0 8px 24px rgba(9, 7, 125, 0.35)', fontWeight: '500' }}
        >
          Ver Roteiro Completo
        </button>
      </motion.div>
    </div>
  );
}
