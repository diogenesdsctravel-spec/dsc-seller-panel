interface Hotel {
  cidade?: string;
  [key: string]: any;
}

interface TripData {
  hoteis?: Hotel[];
  [key: string]: any;
}

interface CityInfo {
  name: string;
  description: string;
}

/**
 * Extrai APENAS cidades onde tem HOTEL reservado
 */
export function extractCities(tripData: TripData): CityInfo[] {
  const cities: CityInfo[] = [];
  const citiesSet = new Set<string>();

  // Pegar apenas cidades com hotel
  if (tripData.hoteis && Array.isArray(tripData.hoteis)) {
    tripData.hoteis.forEach((hotel) => {
      if (hotel.cidade) {
        const cityName = hotel.cidade.trim();

        // Evitar duplicatas
        if (!citiesSet.has(cityName)) {
          citiesSet.add(cityName);
          cities.push({
            name: cityName,
            description: getCityDescription(cityName),
          });
        }
      }
    });
  }

  return cities;
}

/**
 * Retorna descrição da cidade
 */
function getCityDescription(cityName: string): string {
  const descriptions: Record<string, string> = {
    "Lima": "Capital do Peru • Costa do Pacífico",
    "Cusco": "Antiga capital Inca • 3.400m de altitude",
    "Machu Picchu": "Maravilha do Mundo • Patrimônio da UNESCO",
    "Santiago": "Capital do Chile • Vale Central",
    "Buenos Aires": "Capital da Argentina • Patrimônio Cultural",
    "São Paulo": "Maior cidade do Brasil • Hub econômico",
    "Rio de Janeiro": "Cidade Maravilhosa • Praias icônicas",
    "Brasília": "Capital do Brasil • Arquitetura modernista",
    "Salvador": "Primeira capital • Patrimônio Cultural",
  };

  return descriptions[cityName] || "Destino único da sua viagem";
}