import { useState } from "react";
import { Smartphone } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

type PreviewScreen = 'hero' | 'roteiro' | 'voos' | 'hoteis' | 'orcamento';

export function AppPreview() {
    const [previewScreen, setPreviewScreen] = useState<PreviewScreen>('hero');

    return (
        <Card className="shadow-[0_4px_20px_rgba(0,0,0,0.04)]">
            <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                    <Smartphone className="w-5 h-5 text-[#09077D]" />
                    <CardTitle className="text-lg font-normal">Preview do App</CardTitle>
                </div>
                <p className="text-sm text-gray-600">
                    Veja como o cliente receberá a apresentação
                </p>
            </CardHeader>
            <CardContent>
                {/* Tabs */}
                <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
                    {[
                        { id: 'hero', label: 'Boas-vindas' },
                        { id: 'roteiro', label: 'Roteiro' },
                        { id: 'voos', label: 'Voos' },
                        { id: 'hoteis', label: 'Hotéis' },
                        { id: 'orcamento', label: 'Orçamento' }
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setPreviewScreen(tab.id as PreviewScreen)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${previewScreen === tab.id
                                    ? 'bg-[#09077D] text-white'
                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* iPhone Frame */}
                <div className="flex justify-center">
                    <div className="relative">
                        {/* iPhone 14 Pro Shell */}
                        <div className="w-[280px] h-[570px] bg-neutral-900 rounded-[40px] p-3 shadow-2xl">
                            {/* Screen */}
                            <div className="w-full h-full bg-white rounded-[32px] overflow-hidden relative">
                                {/* Dynamic Island */}
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[100px] h-[30px] bg-black rounded-b-[20px] z-10" />

                                {/* Content */}
                                <div className="h-full overflow-y-auto">
                                    {previewScreen === 'hero' && (
                                        <div className="relative h-full">
                                            <div className="h-[240px] bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center">
                                                <p className="text-white text-[20px] font-semibold px-6 text-center">
                                                    Kennedy, prepare-se para viver o Peru.
                                                </p>
                                            </div>
                                            <div className="p-4">
                                                <p className="text-[11px] text-gray-600 mb-3">
                                                    Sua jornada personalizada
                                                </p>
                                                <div className="bg-white rounded-xl p-3 mb-2 shadow-sm border border-gray-100">
                                                    <p className="text-[11px] text-[#09077D] font-medium">
                                                        📍 Lima • Cusco • Machu Picchu
                                                    </p>
                                                </div>
                                                <div className="bg-white rounded-xl p-3 shadow-sm border border-gray-100">
                                                    <p className="text-[11px] text-[#09077D] font-medium">
                                                        🗓️ 8 dias • 7 noites
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {previewScreen === 'roteiro' && (
                                        <div className="p-4 pt-12">
                                            <h2 className="text-[18px] font-semibold text-[#09077D] mb-3">
                                                Roteiro
                                            </h2>
                                            <div className="space-y-2">
                                                {['15/02 — Chegada a Lima', '16/02 — Centro Histórico', '17/02 — Barranco', '18/02 — Voo para Cusco', '19/02 — City Tour', '20/02 — Vale Sagrado', '21/02 — Machu Picchu', '22/02 — Retorno'].map((dia, i) => (
                                                    <div key={i} className="bg-white rounded-lg p-3 shadow-sm border border-gray-100">
                                                        <p className="text-[11px] font-medium text-[#09077D]">
                                                            Dia {i + 1}
                                                        </p>
                                                        <p className="text-[10px] text-gray-600 mt-0.5">
                                                            {dia}
                                                        </p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {previewScreen === 'voos' && (
                                        <div className="p-4 pt-12">
                                            <h2 className="text-[18px] font-semibold text-[#09077D] mb-3">
                                                Voos
                                            </h2>
                                            <div className="space-y-2">
                                                {[
                                                    { rota: 'GRU → LIM', data: '15/02 • 09:15' },
                                                    { rota: 'LIM → CUZ', data: '18/02 • 17:55' },
                                                    { rota: 'CUZ → LIM', data: '22/02 • 12:10' },
                                                    { rota: 'LIM → GRU', data: '22/02 • 21:35' }
                                                ].map((voo, i) => (
                                                    <div key={i} className="bg-white rounded-lg p-3 shadow-sm border border-gray-100">
                                                        <p className="text-[11px] font-medium text-[#09077D]">{voo.rota}</p>
                                                        <p className="text-[10px] text-gray-600">{voo.data}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {previewScreen === 'hoteis' && (
                                        <div className="p-4 pt-12">
                                            <h2 className="text-[18px] font-semibold text-[#09077D] mb-3">
                                                Hotéis
                                            </h2>
                                            <div className="space-y-3">
                                                <div className="bg-white rounded-lg overflow-hidden shadow-sm border border-gray-100">
                                                    <div className="h-[80px] bg-gradient-to-br from-gray-300 to-gray-200" />
                                                    <div className="p-3">
                                                        <p className="text-[11px] font-medium text-[#09077D] mb-1">
                                                            Costa del Sol — Lima
                                                        </p>
                                                        <p className="text-[10px] text-gray-600">
                                                            15-18/02 • 3 noites<br />
                                                            ⭐ 8,4 (Booking)
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="bg-white rounded-lg overflow-hidden shadow-sm border border-gray-100">
                                                    <div className="h-[80px] bg-gradient-to-br from-gray-300 to-gray-200" />
                                                    <div className="p-3">
                                                        <p className="text-[11px] font-medium text-[#09077D] mb-1">
                                                            Tierra Viva — Cusco
                                                        </p>
                                                        <p className="text-[10px] text-gray-600">
                                                            18-22/02 • 4 noites<br />
                                                            ⭐ 8,8 (Booking)
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {previewScreen === 'orcamento' && (
                                        <div className="p-4 pt-12">
                                            <h2 className="text-[18px] font-semibold text-[#09077D] mb-3">
                                                Orçamento
                                            </h2>
                                            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 mb-3">
                                                <p className="text-[10px] text-gray-600 mb-1">Pacote Aéreo + Hotel</p>
                                                <p className="text-[20px] font-semibold text-[#09077D]">
                                                    R$ 6.656
                                                </p>
                                                <p className="text-[10px] text-gray-600 mt-2">
                                                    ✓ Voos • ✓ Hotéis
                                                </p>
                                            </div>
                                            <p className="text-[12px] font-medium text-[#09077D] mb-2">Opcionais</p>
                                            <div className="space-y-1.5">
                                                <div className="flex justify-between text-[10px]">
                                                    <span className="text-gray-600">Transfers</span>
                                                    <span className="text-[#09077D] font-medium">R$ 119,50</span>
                                                </div>
                                                <div className="flex justify-between text-[10px]">
                                                    <span className="text-gray-600">Passeios</span>
                                                    <span className="text-[#09077D] font-medium">R$ 2.325</span>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* iPhone Buttons */}
                        <div className="absolute -left-[1.5px] top-[92px] w-[2px] h-[32px] bg-neutral-800 rounded-l-sm" />
                        <div className="absolute -left-[1.5px] top-[138px] w-[2px] h-[32px] bg-neutral-800 rounded-l-sm" />
                        <div className="absolute -left-[1.5px] top-[178px] w-[2px] h-[32px] bg-neutral-800 rounded-l-sm" />
                        <div className="absolute -right-[1.5px] top-[132px] w-[2px] h-[60px] bg-neutral-800 rounded-r-sm" />
                    </div>
                </div>

                <p className="text-[12px] text-center text-gray-500 mt-4">
                    Atualiza em tempo real conforme você edita
                </p>
            </CardContent>
        </Card>
    );
}