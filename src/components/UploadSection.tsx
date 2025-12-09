import { useState, useRef } from "react";
import { Upload, FileText, Check, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { uploadFiles } from "../services/uploadService";
import { extractTripData } from "../services/extractService";

interface UploadedFile {
    id: number;
    name: string;
    size: string;
    file?: File;
}

interface UploadSectionProps {
    onUploadSuccess?: (tripId: string) => void;
    onRefetch?: () => void;
}

export function UploadSection({ onUploadSuccess, onRefetch }: UploadSectionProps) {
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return (
            Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
        );
    };

    const handleFileSelect = (files: FileList | null) => {
        if (!files) return;

        const newFiles: UploadedFile[] = Array.from(files).map(
            (file, index) => ({
                id: Date.now() + index,
                name: file.name,
                size: formatFileSize(file.size),
                file: file,
            })
        );

        setUploadedFiles((prev) => [...prev, ...newFiles]);
        setError(null);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        handleFileSelect(e.dataTransfer.files);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
    };

    const handleUpload = async () => {
        if (uploadedFiles.length === 0) return;

        setUploading(true);
        setError(null);

        try {
            const files = uploadedFiles.map((f) => f.file!).filter(Boolean);
            const uploadResponse = await uploadFiles(files);

            console.log("✅ Upload concluído! Trip ID:", uploadResponse.trip_id);

            console.log("🤖 Iniciando extração com IA...");
            const extractResponse = await extractTripData(uploadResponse.trip_id);

            console.log("✅ Extração concluída!", extractResponse);

            if (onUploadSuccess) {
                onUploadSuccess(uploadResponse.trip_id);
            }

            setTimeout(() => {
                if (onRefetch) {
                    onRefetch();
                }
            }, 1000);

        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Erro ao processar arquivos"
            );
        } finally {
            setUploading(false);
        }
    };

    return (
        <Card className="shadow-[0_4px_20px_rgba(0,0,0,0.04)]">
            <CardHeader className="pb-3">
                <CardTitle className="text-lg font-semibold text-[#09077D]">
                    1. Envie os arquivos
                </CardTitle>
                <p className="text-sm text-gray-600">
                    Envie o orçamento em PDF ou prints. Nossa IA organizará tudo automaticamente.
                </p>
            </CardHeader>
            <CardContent className="space-y-6">
                <div
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center hover:border-[#50CFAD] hover:bg-[#50CFAD]/5 transition-all duration-300 cursor-pointer"
                >
                    <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
                        <Upload className="w-8 h-8 text-[#09077D]" />
                    </div>
                    <p className="text-[15px] font-medium text-[#09077D] mb-2">
                        Arraste arquivos aqui
                    </p>
                    <p className="text-[13px] text-gray-500 mb-4">
                        ou clique para selecionar
                    </p>
                    <button
                        type="button"
                        className="px-6 py-2 bg-[#09077D] text-white rounded-xl text-sm font-medium hover:scale-105 transition-transform"
                    >
                        Selecionar arquivos
                    </button>
                </div>

                <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => handleFileSelect(e.target.files)}
                    className="hidden"
                />

                {uploadedFiles.length > 0 && (
                    <div>
                        <h3 className="text-[15px] font-semibold text-[#09077D] mb-3">
                            Arquivos selecionados ({uploadedFiles.length})
                        </h3>
                        <div className="space-y-2">
                            {uploadedFiles.map((file) => (
                                <div
                                    key={file.id}
                                    className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl"
                                >
                                    <div className="w-10 h-10 rounded-lg bg-white border border-gray-200 flex items-center justify-center flex-shrink-0">
                                        <FileText className="w-5 h-5 text-[#09077D]" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-[13px] font-medium text-[#09077D] truncate">
                                            {file.name}
                                        </p>
                                        <p className="text-[12px] text-gray-500">
                                            {file.size}
                                        </p>
                                    </div>
                                    <div className="w-6 h-6 rounded-full bg-[#50CFAD]/10 flex items-center justify-center flex-shrink-0">
                                        <Check className="w-4 h-4 text-[#50CFAD]" />
                                    </div>
                                </div>
                            ))}
                        </div>

                        <button
                            onClick={handleUpload}
                            disabled={uploading}
                            className="w-full mt-4 px-6 py-3 bg-[#09077D] text-white rounded-xl text-sm font-medium hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {uploading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Enviando...
                                </>
                            ) : (
                                "Processar com IA"
                            )}
                        </button>
                    </div>
                )}

                {error && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                        {error}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
