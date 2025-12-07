import { useState } from "react";
import { Upload, FileText, Check } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface UploadedFile {
    id: number;
    name: string;
    size: string;
}

export function UploadSection() {
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([
        { id: 1, name: 'Roteiro_Peru_Kennedy.pdf', size: '2.4 MB' },
        { id: 2, name: 'Hoteis_Lima_Cusco.pdf', size: '1.8 MB' }
    ]);

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
                {/* Drag & Drop Area */}
                <div className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center hover:border-[#50CFAD] hover:bg-[#50CFAD]/5 transition-all duration-300 cursor-pointer">
                    <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
                        <Upload className="w-8 h-8 text-[#09077D]" />
                    </div>
                    <p className="text-[15px] font-medium text-[#09077D] mb-2">
                        Arraste arquivos aqui
                    </p>
                    <p className="text-[13px] text-gray-500 mb-4">
                        ou clique para selecionar
                    </p>
                    <button className="px-6 py-2 bg-[#09077D] text-white rounded-xl text-sm font-medium hover:scale-105 transition-transform">
                        Selecionar arquivos
                    </button>
                </div>

                {/* Lista de Arquivos Enviados */}
                {uploadedFiles.length > 0 && (
                    <div>
                        <h3 className="text-[15px] font-semibold text-[#09077D] mb-3">
                            Arquivos enviados ({uploadedFiles.length})
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
                    </div>
                )}
            </CardContent>
        </Card>
    );
}