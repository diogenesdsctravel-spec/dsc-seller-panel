import { useState } from "react";
import { Smartphone } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

type PreviewScreen = "hero" | "roteiro" | "voos" | "hoteis" | "orcamento";

interface AppPreviewProps {
    tripData?: any;
}

export function AppPreview({ tripData }: AppPreviewProps) {
    const [previewScreen, setPreviewScreen] = useState<PreviewScreen>("hero");

    // Fallbacks + dados reais
    const cliente: string = tripData?.cliente || "Cliente";

    const destinoPrincipal: string =
        tripData?.destinoPrincipal || tripData?.destino || "Peru";

    const cidadesLinha: string =
        Array.isArray(tripData?.cidades) && tripData.cidades.length > 0
            ? tripData.cidades.join(" • ")
            : "Lima • Cusco • Machu Picchu";

    const diasNoitesResumo: string =
        tripData?.resumoDuracao || tripData?.duracao || "8 dias • 7 noites";

    const roteiroItems =
        Array.isArray(tripData?.roteiro) && tripData.roteiro.length > 0
            ? tripData.roteiro
            : [
                "15/02 — Chegada a Lima",
                "16/02 — Centro Histórico",
                "17/02 — Barranco",
                "18/02 — Voo para Cusco",
                "19/02 — City Tour",
                "20/02 — Vale Sagrado",
                "21/02 — Machu Picchu",
                "22/02 — Retorno",
            ];

    const voos =
        Array.isArray(tripData?.voos) && tripData.voos.length > 0
            ? tripData.voos
            : [
                { rota: "GRU → LIM", data: "15/02 • 09:15" },
                { rota: "LIM → CUZ", data: "18/02 • 17:55" },
                { rota: "CUZ → LIM", data: "22/02 • 12:10" },
                { rota: "LIM → GRU", data: "22/02 • 21:35" },
            ];

    const hoteis =
        Array.isArray(tripData?.hoteis) && tripData.hoteis.length > 0
            ? tripData.hoteis
            : [
                {
                    nome: "Costa del Sol",
                    cidade: "Lima",
                    checkin: "15/02",
                    checkout: "18/02",
                    noites: 3,
                    nota: "8,4",
                    origemNota: "Booking",
                },
                {
                    nome: "Tierra Viva",
                    cidade: "Cusco",
                    checkin: "18/02",
                    checkout: "22/02",
                    noites: 4,
                    nota: "8,8",
                    origemNota: "Booking",
                },
            ];

    const orcamentoPrincipal = tripData?.orcamento?.pacotePrincipal || {
        titulo: "Pacote Aéreo + Hotel",
        valor: "R$ 6.656",
        descricao: "✓ Voos • ✓ Hotéis",
    };

    const orcamentoOpcionais =
        Array.isArray(tripData?.orcamento?.opcionais) &&
            tripData.orcamento.opcionais.length > 0
            ? tripData.orcamento.opcionais
            : [
                { titulo: "Transfers", valor: "R$ 119,50" },
                { titulo: "Passeios", valor: "R$ 2.325" },
            ];

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
                        { id: "hero", label: "Boas-vindas" },
                        { id: "roteiro", label: "Roteiro" },
                        { id: "voos", label: "Voos" },
                        { id: "hoteis", label: "Hotéis" },
                        { id: "orcamento", label: "Orçamento" },
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setPreviewScreen(tab.id as PreviewScreen)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${previewScreen === tab.id
                                    ? "bg-[#09077D] text-white"
                                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
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
                                    {previewScreen === "hero" && (
                                        <div className="relative h-full">
                                            <div className="h-[240px] bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center">
                                                <p className="text-white text-[20px] font-semibold px-6 text-center">
                                                    {cliente}, prepare-se para viver{" "}
                                                    {hoteis[0]?.cidade || "sua viagem"}.
                                                </p>
                                            </div>
                                            <div className="p-4">
                                                <p className="text-[11px] text-gray-600 mb-3">
                                                    Sua jornada personalizada
                                                </p>
                                                <div className="bg-white rounded-xl p-3 mb-2 shadow-sm border border-gray-100">
                                                    <p className="text-[11px] text-[#09077D] font-medium">
                                                        📍{" "}
                                                        {hoteis
                                                            .map((h: any) => h.cidade)
                                                            .filter(Boolean)
                                                            .join(" • ") || "Destinos"}
                                                    </p>
                                                </div>
                                                <div className="bg-white rounded-xl p-3 shadow-sm border border-gray-100">
                                                    <p className="text-[11px] text-[#09077D] font-medium">
                                                        🗓️ {tripData?.periodo?.inicio || "Data"} -{" "}
                                                        {tripData?.periodo?.fim || "Data"}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {previewScreen === "roteiro" && (
                                        <div className="p-4 pt-12">
                                            <h2 className="text-[18px] font-semibold text-[#09077D] mb-3">
                                                Roteiro
                                            </h2>
                                            <div className="space-y-2">
                                                {roteiroItems.map((dia: any, i: number) => {
                                                    const tituloDia =
                                                        typeof dia === "string"
                                                            ? dia
                                                            : dia?.titulo || dia?.resumo || "";
                                                    const descricaoDia =
                                                        typeof dia === "string"
                                                            ? ""
                                                            : dia?.descricao || dia?.detalhes || "";

                                                    return (
                                                        <div
                                                            key={i}
                                                            className="bg-white rounded-lg p-3 shadow-sm border border-gray-100"
                                                        >
                                                            <p className="text-[11px] font-medium text-[#09077D]">
                                                                Dia {i + 1}
                                                            </p>
                                                            <p className="text-[10px] text-gray-600 mt-0.5">
                                                                {tituloDia}
                                                            </p>
                                                            {descricaoDia && (
                                                                <p className="text-[10px] text-gray-500 mt-0.5">
                                                                    {descricaoDia}
                                                                </p>
                                                            )}
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}

                                    {previewScreen === "voos" && (
                                        <div className="p-4 pt-12">
                                            <h2 className="text-[18px] font-semibold text-[#09077D] mb-3">
                                                Voos
                                            </h2>
                                            <div className="space-y-2">
                                                {voos.map((voo: any, i: number) => {
                                                    const rota =
                                                        voo?.rota ||
                                                        (voo?.origem && voo?.destino
                                                            ? `${voo.origem} → ${voo.destino}`
                                                            : "Voo");
                                                    const dataLinha =
                                                        voo?.data ||
                                                        voo?.dataHorario ||
                                                        [voo?.dataPartida, voo?.horarioPartida]
                                                            .filter(Boolean)
                                                            .join(" • ");

                                                    return (
                                                        <div
                                                            key={i}
                                                            className="bg-white rounded-lg p-3 shadow-sm border border-gray-100"
                                                        >
                                                            <p className="text-[11px] font-medium text-[#09077D]">
                                                                {rota}
                                                            </p>
                                                            {dataLinha && (
                                                                <p className="text-[10px] text-gray-600">
                                                                    {dataLinha}
                                                                </p>
                                                            )}
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}

                                    {previewScreen === "hoteis" && (
                                        <div className="p-4 pt-12">
                                            <h2 className="text-[18px] font-semibold text-[#09077D] mb-3">
                                                Hotéis
                                            </h2>
                                            <div className="space-y-3">
                                                {hoteis.map((hotel: any, i: number) => {
                                                    const nome =
                                                        hotel?.nome ||
                                                        hotel?.hotel ||
                                                        `${hotel?.nomeHotel || ""}`;
                                                    const cidade = hotel?.cidade || hotel?.local || "";
                                                    const checkin = hotel?.checkin || hotel?.inicio || "";
                                                    const checkout =
                                                        hotel?.checkout || hotel?.fim || "";
                                                    const noites =
                                                        hotel?.noites ??
                                                        hotel?.qtdeNoites ??
                                                        hotel?.noitesTotal;
                                                    const nota = hotel?.nota || hotel?.score;
                                                    const origemNota =
                                                        hotel?.origemNota || hotel?.fonteNota || "Booking";

                                                    const periodo =
                                                        checkin && checkout
                                                            ? `${checkin} - ${checkout}`
                                                            : "";

                                                    return (
                                                        <div
                                                            key={i}
                                                            className="bg-white rounded-lg overflow-hidden shadow-sm border border-gray-100"
                                                        >
                                                            <div className="h-[80px] bg-gradient-to-br from-gray-300 to-gray-200" />
                                                            <div className="p-3">
                                                                <p className="text-[11px] font-medium text-[#09077D] mb-1">
                                                                    {nome}
                                                                    {cidade ? ` — ${cidade}` : ""}
                                                                </p>
                                                                <p className="text-[10px] text-gray-600">
                                                                    {periodo && `${periodo} • `}
                                                                    {noites && `${noites} noites`}
                                                                    <br />
                                                                    {nota && (
                                                                        <>
                                                                            ⭐ {nota} ({origemNota})
                                                                        </>
                                                                    )}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}

                                    {previewScreen === "orcamento" && (
                                        <div className="p-4 pt-12">
                                            <h2 className="text-[18px] font-semibold text-[#09077D] mb-3">
                                                Orçamento
                                            </h2>
                                            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 mb-3">
                                                <p className="text-[10px] text-gray-600 mb-1">
                                                    {orcamentoPrincipal.titulo ||
                                                        "Pacote Aéreo + Hotel"}
                                                </p>
                                                <p className="text-[20px] font-semibold text-[#09077D]">
                                                    {orcamentoPrincipal.valor || "R$ 0,00"}
                                                </p>
                                                {orcamentoPrincipal.descricao && (
                                                    <p className="text-[10px] text-gray-600 mt-2">
                                                        {orcamentoPrincipal.descricao}
                                                    </p>
                                                )}
                                            </div>
                                            <p className="text-[12px] font-medium text-[#09077D] mb-2">
                                                Opcionais
                                            </p>
                                            <div className="space-y-1.5">
                                                {orcamentoOpcionais.map((opt: any, i: number) => (
                                                    <div
                                                        key={i}
                                                        className="flex justify-between text-[10px]"
                                                    >
                                                        <span className="text-gray-600">
                                                            {opt.titulo || opt.nome || "Opcional"}
                                                        </span>
                                                        <span className="text-[#09077D] font-medium">
                                                            {opt.valor || "R$ 0,00"}
                                                        </span>
                                                    </div>
                                                ))}
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
