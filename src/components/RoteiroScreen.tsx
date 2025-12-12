import { useState } from "react";
import { motion } from "framer-motion";

interface DiaRoteiro {
    dia: number;
    data: string;
    titulo: string;
    horario?: string;
    descricao: string;
    transfer?: "incluido" | "a-incluir" | null;
    dica?: string;
}

interface RoteiroScreenProps {
    dias: DiaRoteiro[];
    imagensCidades: Record<string, string[]>;
    onBack: () => void; // usado no botão "Voltar ao Início"
}

export function RoteiroScreen({
    dias,
    imagensCidades,
    onBack,
}: RoteiroScreenProps) {
    const [diaAtual, setDiaAtual] = useState(0);

    if (!dias?.length) {
        return (
            <div className="px-6 pt-16 pb-8 bg-[#F7F7F7] min-h-full">
                <h1 className="text-[32px] mb-3" style={{ color: "#09077D" }}>
                    Roteiro
                </h1>
                <p className="text-gray-700">Gerando roteiro...</p>
            </div>
        );
    }

    const dia = dias[diaAtual];
    const proximoDia =
        diaAtual < dias.length - 1 ? dias[diaAtual + 1] : null;

    const todasFotos = Object.values(imagensCidades).flat();
    const imagemUrl =
        todasFotos[diaAtual % (todasFotos.length || 1)] ||
        "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200";

    return (
        <div className="bg-[#F7F7F7] min-h-full">
            <motion.div
                key={diaAtual}
                className="relative h-[450px]"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6 }}
            >
                <img
                    src={imagemUrl}
                    alt={dia.titulo}
                    className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/60" />

                <div className="absolute bottom-8 left-6 right-6">
                    <h1
                        className="text-white text-[40px] leading-[1.05] mb-2"
                        style={{
                            letterSpacing: "-0.03em",
                            textShadow: "0 2px 12px rgba(0,0,0,0.3)",
                        }}
                    >
                        Dia {dia.dia} — {dia.data}
                    </h1>
                    <p
                        className="text-white text-[24px]"
                        style={{ textShadow: "0 1px 8px rgba(0,0,0,0.3)" }}
                    >
                        {dia.titulo}
                    </p>
                </div>
            </motion.div>

            <div className="px-6 pt-8 pb-8">
                {dia.horario && (
                    <h3
                        className="text-[20px] mb-6"
                        style={{ color: "#09077D", fontWeight: "600" }}
                    >
                        {dia.horario}
                    </h3>
                )}

                <div className="bg-white rounded-[20px] p-5 mb-6 shadow-[0_8px_20px_rgba(0,0,0,0.06)]">
                    <p className="text-[15px] leading-[1.6] text-gray-700 whitespace-pre-line">
                        {dia.descricao}
                    </p>

                    {dia.transfer && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                            <p
                                className="text-[14px]"
                                style={{ color: "#09077D", fontWeight: "500" }}
                            >
                                ✓ Transfer{" "}
                                {dia.transfer === "incluido" ? "incluído" : "a incluir"}
                            </p>
                        </div>
                    )}
                </div>

                {dia.dica && (
                    <div
                        className="rounded-[20px] p-5 mb-8"
                        style={{ background: "#50CFAD" }}
                    >
                        <h3
                            className="text-white text-[17px] mb-2"
                            style={{ fontWeight: "600" }}
                        >
                            Dica DSC Travel
                        </h3>
                        <p className="text-white text-[15px] leading-[1.6]">
                            {dia.dica}
                        </p>
                    </div>
                )}

                <button
                    onClick={() =>
                        proximoDia ? setDiaAtual(diaAtual + 1) : onBack()
                    }
                    className="w-full px-8 py-5 text-white rounded-[16px] text-[17px] transition-all"
                    style={{
                        background: "#09077D",
                        boxShadow: "0 8px 24px rgba(9, 7, 125, 0.35)",
                        fontWeight: "500",
                    }}
                >
                    {proximoDia ? proximoDia.titulo : "← Voltar ao Início"}
                </button>
            </div>
        </div>
    );
}
