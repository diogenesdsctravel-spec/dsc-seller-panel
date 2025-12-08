const API_BASE_URL = import.meta.env.VITE_API_URL || "https://api.dsctravel.com.br";

export interface UploadResponse {
    trip_id: string;
    status: string;
    message: string;
    files: string[];
}

export async function uploadFiles(files: File[]): Promise<UploadResponse> {
    const formData = new FormData();

    files.forEach((file) => {
        formData.append("files", file);
    });

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Erro ao fazer upload. Status ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Erro em uploadFiles:", error);
        throw error;
    }
}