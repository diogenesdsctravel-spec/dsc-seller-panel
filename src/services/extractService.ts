const API_BASE_URL = import.meta.env.VITE_API_URL || "https://api.dsctravel.com.br";

export interface ExtractResponse {
    trip_id: string;
    status: string;
    message: string;
}

export async function extractTripData(tripId: string, nomeCliente?: string): Promise<ExtractResponse> {
    try {
        const response = await fetch(`${API_BASE_URL}/extract/${tripId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                cliente_nome: nomeCliente || ""
            }),
        });

        if (!response.ok) {
            throw new Error(`Erro ao extrair dados. Status ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Erro em extractTripData:", error);
        throw error;
    }
}