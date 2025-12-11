// src/components/AppPreview.tsx
import { useState } from "react";
import { Smartphone, MapPin, Clock } from "lucide-react";
import { motion } from "framer-motion";
import { extractCities } from "../utils/extractCities";
import { CidadesIncluidas } from "./CidadesIncluidas";
import { RoteiroScreen } from "./RoteiroScreen";
import { BottomNavigation } from "./BottomNavigation";

type PreviewScreen = "hero" | "voos" | "hoteis";
type BottomTab = "inicio" | "roteiro" | "produtos" | "orcamento" | "conta";

interface AppPreviewProps {
    tripData?: any;
}

export function AppPreview({ tripData }: AppPreviewProps) {
    const [previewScreen, setPreviewScreen] = useState<PreviewScreen>("hero");
    const [currentScreen, setCurrentScreen] = useState<"hero" | "cidades" | "roteiro">("hero");

    // controla qual aba está ativa na barra inferior
    const [activeTab, setActiveTab] = useState<BottomTab>("roteiro");

    const cities = extractCities(tripData || {});

    const citiesWithImages = cities.map((city, index) => ({
        ...city,
        imageUrl:
            index === 0 && tripData?.imagem_hero
                ? tripData.imagem_hero
                : `https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80`,
    }));

    const cliente = tripData?.cliente || "Cliente";
    const imagemHero = tripData?.imagem_hero;

    const destinos =
        tripData?.hoteis?.map((h: any) => h.cidade).filter(Boolean) || [];
    const destinosTexto =
        destinos.length > 0 ? destinos.join(" • ") : "Destinos";

    const periodoInicio = tripData?.periodo?.inicio || "Data";
    const periodoFim = tripData?.periodo?.fim || "Data";

    const totalNoites =
        tripData?.hoteis?.reduce(
            (sum: number, h: any) => sum + (h.noites || 0),
            0
        ) || 0;
    const duracaoTexto =
        totalNoites > 0
            ? `${totalNoites + 1} dias • ${totalNoites} noites`
            : "8 dias • 7 noites";

    const voos = tripData?.voos || [];
    const hoteis = tripData?.hoteis || [];

    // quando o usuário toca em uma aba da BottomNavigation
    function handleTabChange(tabId: BottomTab) {
        setActiveTab(tabId);

        if (tabId === "inicio") {
            // voltar para a PRIMEIRA TELA
            setPreviewScreen("hero");
            setCurrentScreen("hero");
        }

        if (tabId === "roteiro") {
            // se quiser, podemos forçar ir direto para o roteiro
            setPreviewScreen("hero");
            setCurrentScreen("roteiro");
        }

        // por enquanto, produtos / orçamento / conta não navegam
        // (você pode ligar depois para outras telas se quiser)
    }

    return (
        <div className="flex flex-col">
            <div className="flex items-center gap-3 mb-4">
                <Smartphone className="w-5 h-5 text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-900">
                    Pré-visualização do aplicativo
                </h2>
            </div>

            <p className="text-sm text-gray-600 mb-6">
                Veja como o cliente receberá uma apresentação mobile profissional
            </p>

            <div className="relative mx-auto">
                <div
                    className="relative bg-black rounded-[52px] p-2 shadow-2xl"
                    style={{ width: "393px", height: "852px" }}
                >
                    <div className="relative w-full h-full bg-[#F7F7F7] rounded-[44px] overflow-hidden flex flex-col">
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 z-50 w-[126px] h-[37px] bg-black rounded-full" />

                        {/* Área rolável das telas */}
                        <div className="flex-1 relative w-full overflow-y-auto">
                            {previewScreen === "hero" && (
                                <>
                                    {currentScreen === "hero" && (
                                        <>
                                            <div className="relative h-[450px] overflow-hidden rounded-b-[32px]">
                                                {imagemHero ? (
                                                    <img
                                                        src={imagemHero}
                                                        alt="Destino"
                                                        className="w-full h-full object-cover"
                                                    />
                                                ) : (
                                                    <div className="w-full h-full bg-gradient-to-br from-blue-500 to-cyan-400" />
                                                )}

                                                <div className="absolute inset-0 bg-black/30" />
                                                <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/60" />

                                                <div className="absolute bottom-8 left-6 right-6">
                                                    <h1
                                                        className="text-white text-[40px] leading-[1.05] mb-3"
                                                        style={{
                                                            letterSpacing: "-0.03em",
                                                            textShadow:
                                                                "0 2px 12px rgba(0,0,0,0.3)",
                                                        }}
                                                    >
                                                        {cliente}, prepare-se
                                                        <br />
                                                        para viver{" "}
                                                        {destinos[0] || "sua viagem"}.
                                                    </h1>
                                                    <p
                                                        className="text-white/90 text-[17px] leading-[1.4]"
                                                        style={{
                                                            textShadow:
                                                                "0 1px 8px rgba(0,0,0,0.3)",
                                                        }}
                                                    >
                                                        Sua jornada personalizada
                                                    </p>
                                                </div>
                                            </div>

                                            <div className="px-6 pt-8 pb-[120px]">
                                                <h2
                                                    className="text-[24px] mb-4"
                                                    style={{ color: "#09077D" }}
                                                >
                                                    Sua viagem premium
                                                </h2>

                                                <p className="text-[16px] leading-[1.5] text-gray-700 mb-8">
                                                    Uma experiência personalizada com todo conforto e
                                                    sofisticação que você merece.
                                                </p>

                                                <div className="space-y-4">
                                                    <div className="bg-white rounded-[20px] p-5 flex items-center gap-4 shadow-[0_8px_20px_rgba(0,0,0,0.06)]">
                                                        <div
                                                            className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                                                            style={{
                                                                background: "#50CFAD",
                                                            }}
                                                        >
                                                            <MapPin className="w-6 h-6 text-white" />
                                                        </div>
                                                        <div>
                                                            <p
                                                                className="text-[13px]"
                                                                style={{ color: "#6B7280" }}
                                                            >
                                                                Destinos
                                                            </p>
                                                            <p
                                                                className="text-[17px]"
                                                                style={{ color: "#09077D" }}
                                                            >
                                                                {destinosTexto}
                                                            </p>
                                                        </div>
                                                    </div>

                                                    <div className="bg-white rounded-[20px] p-5 flex items-center gap-4 shadow-[0_8px_20px_rgba(0,0,0,0.06)]">
                                                        <div
                                                            className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                                                            style={{
                                                                background: "#50CFAD",
                                                            }}
                                                        >
                                                            <Clock className="w-6 h-6 text-white" />
                                                        </div>
                                                        <div>
                                                            <p
                                                                className="text-[13px]"
                                                                style={{ color: "#6B7280" }}
                                                            >
                                                                Duração
                                                            </p>
                                                            <p
                                                                className="text-[17px]"
                                                                style={{ color: "#09077D" }}
                                                            >
                                                                {duracaoTexto}
                                                            </p>
                                                        </div>
                                                    </div>

                                                    <div className="bg-white rounded-[20px] p-5 flex items-center gap-4 shadow-[0_8px_20px_rgba(0,0,0,0.06)]">
                                                        <div
                                                            className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 text-[20px]"
                                                            style={{
                                                                background: "#50CFAD",
                                                                color: "white",
                                                            }}
                                                        >
                                                            📅
                                                        </div>
                                                        <div>
                                                            <p
                                                                className="text-[13px]"
                                                                style={{ color: "#6B7280" }}
                                                            >
                                                                Período
                                                            </p>
                                                            <p
                                                                className="text-[17px]"
                                                                style={{ color: "#09077D" }}
                                                            >
                                                                {periodoInicio} - {periodoFim}
                                                            </p>
                                                        </div>
                                                    </div>
                                                </div>

                                                <button
                                                    onClick={() => {
                                                        setCurrentScreen("cidades");
                                                        setActiveTab("roteiro");
                                                    }}
                                                    className="w-full mt-8 text-white rounded-[16px] px-8 py-5 text-[17px] transition-all"
                                                    style={{
                                                        background: "#09077D",
                                                        boxShadow:
                                                            "0 8px 24px rgba(9, 7, 125, 0.35)",
                                                    }}
                                                >
                                                    Ver Detalhes da Viagem
                                                </button>
                                            </div>
                                        </>
                                    )}

                                    {currentScreen === "cidades" && (
                                        <CidadesIncluidas
                                            cities={citiesWithImages}
                                            onBack={() => {
                                                setCurrentScreen("hero");
                                                setActiveTab("inicio");
                                            }}
                                            onVerRoteiro={() => {
                                                setCurrentScreen("roteiro");
                                                setActiveTab("roteiro");
                                            }}
                                        />
                                    )}

                                    {currentScreen === "roteiro" && (
                                        <RoteiroScreen
                                            dias={tripData?.roteiro || []}
                                            imagensCidades={tripData?.imagens_cidades || {}}
                                            onBack={() => {
                                                setCurrentScreen("cidades");
                                                setActiveTab("roteiro");
                                            }}
                                        />
                                    )}
                                </>
                            )}

                            {previewScreen === "voos" && (
                                <div className="px-6 pt-16 pb-[120px]">
                                    <button
                                        onClick={() => setPreviewScreen("hero")}
                                        className="text-[15px] mb-6"
                                        style={{ color: "#09077D" }}
                                    >
                                        ← Voltar
                                    </button>

                                    <h1
                                        className="text-[32px] mb-3 leading-[1.1]"
                                        style={{
                                            color: "#09077D",
                                            letterSpacing: "-0.02em",
                                        }}
                                    >
                                        Voos
                                    </h1>
                                    <p className="text-[16px] leading-[1.5] text-gray-700 mb-8">
                                        Todos os trechos da sua viagem
                                    </p>

                                    {voos.length > 0 ? (
                                        <div className="space-y-5">
                                            {voos.map((voo: any, idx: number) => (
                                                <div
                                                    key={idx}
                                                    className="bg-white rounded-[20px] p-5 shadow-[0_8px_20px_rgba(0,0,0,0.06)]"
                                                >
                                                    <div className="flex justify-between items-start mb-4">
                                                        <div>
                                                            <p
                                                                className="text-[14px] mb-1"
                                                                style={{ color: "#6B7280" }}
                                                            >
                                                                {voo.data}
                                                            </p>
                                                            <h3
                                                                className="text-[19px]"
                                                                style={{ color: "#09077D" }}
                                                            >
                                                                {voo.origem} → {voo.destino}
                                                            </h3>
                                                        </div>
                                                        <div className="text-right">
                                                            <p
                                                                className="text-[14px]"
                                                                style={{ color: "#6B7280" }}
                                                            >
                                                                Saída
                                                            </p>
                                                            <p
                                                                className="text-[17px]"
                                                                style={{ color: "#09077D" }}
                                                            >
                                                                {voo.horario_saida}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    {voo.companhia && (
                                                        <p className="text-[15px] text-gray-700">
                                                            {voo.companhia}
                                                        </p>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-gray-500 text-center py-8">
                                            Nenhum voo disponível
                                        </p>
                                    )}
                                </div>
                            )}

                            {previewScreen === "hoteis" && (
                                <div className="px-6 pt-16 pb-[120px]">
                                    <button
                                        onClick={() => setPreviewScreen("hero")}
                                        className="text-[15px] mb-6"
                                        style={{ color: "#09077D" }}
                                    >
                                        ← Voltar
                                    </button>

                                    <h1
                                        className="text-[32px] mb-3 leading-[1.1]"
                                        style={{
                                            color: "#09077D",
                                            letterSpacing: "-0.02em",
                                        }}
                                    >
                                        Hotéis
                                    </h1>
                                    <p className="text-[16px] leading-[1.5] text-gray-700 mb-8">
                                        Acomodações selecionadas
                                    </p>

                                    {hoteis.length > 0 ? (
                                        <div className="space-y-6">
                                            {hoteis.map((hotel: any, idx: number) => (
                                                <div
                                                    key={idx}
                                                    className="bg-white rounded-[20px] p-5 shadow-[0_8px_20px_rgba(0,0,0,0.06)]"
                                                >
                                                    <h3
                                                        className="text-[19px] mb-2"
                                                        style={{ color: "#09077D" }}
                                                    >
                                                        {hotel.nome || "Hotel"}
                                                    </h3>
                                                    <p className="text-[15px] text-gray-700 mb-3">
                                                        <strong>{hotel.cidade}</strong> •{" "}
                                                        {hotel.noites} noites
                                                    </p>
                                                    <p
                                                        className="text-[14px]"
                                                        style={{ color: "#6B7280" }}
                                                    >
                                                        Check-in: {hotel.checkin} | Check-out:{" "}
                                                        {hotel.checkout}
                                                    </p>
                                                    {hotel.regime && (
                                                        <p
                                                            className="text-[14px] mt-2"
                                                            style={{ color: "#6B7280" }}
                                                        >
                                                            {hotel.regime}
                                                        </p>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-gray-500 text-center py-8">
                                            Nenhum hotel disponível
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* BottomNavigation fixa no rodapé do “iPhone” */}
                        <BottomNavigation
                            activeTab={activeTab}
                            onTabChange={handleTabChange}
                        />
                    </div>
                </div>

                <div className="absolute -left-[2px] top-[140px] w-[3px] h-[50px] bg-neutral-800 rounded-l-sm" />
                <div className="absolute -left-[2px] top-[210px] w-[3px] h-[50px] bg-neutral-800 rounded-l-sm" />
                <div className="absolute -left-[2px] top-[270px] w-[3px] h-[50px] bg-neutral-800 rounded-l-sm" />
                <div className="absolute -right-[2px] top-[200px] w-[3px] h-[90px] bg-neutral-800 rounded-r-sm" />
            </div>
        </div>
    );
}
