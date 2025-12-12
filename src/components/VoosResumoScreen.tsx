import { Plane, ChevronLeft } from "lucide-react";
import { motion } from "framer-motion";

interface VoosResumoScreenProps {
  tripData: any;
  onBack: () => void;
  onNavigateToTimeline: (tipo: "ida" | "volta") => void;
  onTabChange?: (tab: string) => void; // pode manter só por compatibilidade, mesmo sem usar
}

export function VoosResumoScreen({
  tripData,
  onBack,
  onNavigateToTimeline,
}: VoosResumoScreenProps) {
  const cliente = tripData?.cliente || "Cliente";
  const voos = tripData?.voos || [];
  const destino = tripData?.hoteis?.[0]?.cidade || "seu destino";
  const imagemDestino =
    tripData?.imagem_hero ||
    "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200";

  // Separar voos de ida e volta
  const voosIda = voos.slice(0, Math.ceil(voos.length / 2));
  const voosVolta = voos.slice(Math.ceil(voos.length / 2));

  const dataIda = voosIda[0]?.data || "Data";
  const dataVolta = voosVolta[0]?.data || "Data";

  return (
    <div className="absolute inset-0 flex flex-col bg-white">
      <div className="flex-1 overflow-y-auto">
        <div className="px-6 pt-16 pb-8">
          {/* Botão Voltar */}
          <button
            onClick={onBack}
            className="flex items-center gap-2 mb-6 text-[#09077D]"
          >
            <ChevronLeft className="w-5 h-5" />
            <span className="text-[15px]">Voltar</span>
          </button>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Título "personalizada" */}
            <motion.p
              className="text-center mb-4 text-[22px] tracking-wide italic"
              style={{
                color: "#09077D",
                fontWeight: "300",
                letterSpacing: "0.5px",
              }}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
            >
              personalizada
            </motion.p>

            {/* Linha de rota + Selo */}
            <div className="flex items-center justify-between gap-4 mb-6">
              {/* Rota simplificada */}
              <motion.div
                className="flex items-center gap-2 flex-1"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <span className="text-[14px] font-medium text-gray-700">
                  {voosIda[0]?.origem?.split("(")[1]?.replace(")", "") ||
                    "Origem"}
                </span>
                <Plane
                  className="w-4 h-4 text-gray-600"
                  style={{ transform: "rotate(45deg)" }}
                />
                <span className="text-[14px] font-medium text-gray-700">
                  {voosIda[voosIda.length - 1]?.destino
                    ?.split("(")[1]
                    ?.replace(")", "") || "Destino"}
                </span>
              </motion.div>

              {/* Selo Premium */}
              <motion.div
                className="relative flex-shrink-0"
                initial={{ opacity: 0, scale: 0.8, rotate: -15 }}
                animate={{ opacity: 1, scale: 1, rotate: 0 }}
                transition={{
                  duration: 0.8,
                  delay: 0.4,
                  type: "spring",
                }}
              >
                <div
                  className="w-[90px] h-[90px] rounded-full border-2 flex items-center justify-center"
                  style={{ borderColor: "#09077D" }}
                >
                  <div className="text-center px-2">
                    <p
                      className="text-[10px] leading-[1.3]"
                      style={{ color: "#09077D", fontWeight: "500" }}
                    >
                      Selecionado
                      <br />
                      para
                      <br />
                      <span className="text-[11px]">{cliente}</span>
                    </p>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Imagem de destino */}
            <motion.div
              className="relative rounded-[20px] overflow-hidden mb-6 shadow-xl"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.7, delay: 0.2 }}
            >
              <div className="relative h-[280px]">
                <img
                  src={imagemDestino}
                  alt={destino}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />

                <div className="absolute bottom-0 left-0 right-0 p-6">
                  <p className="text-white text-[24px] mb-2">
                    Bem-vindo(a) a {destino}!
                  </p>
                  <p className="text-white/90 text-[15px]">
                    Em breve, você estará lá.
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Cards de Voos */}
            <div className="space-y-4">
              {/* Card IDA */}
              <motion.button
                onClick={() => onNavigateToTimeline("ida")}
                className="w-full bg-gradient-to-br from-blue-50 to-white rounded-[16px] p-5 shadow-md border border-blue-100"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                    style={{ background: "#09077D" }}
                  >
                    <Plane
                      className="w-6 h-6 text-white"
                      style={{ transform: "rotate(45deg)" }}
                    />
                  </div>
                  <div className="text-left">
                    <p
                      className="text-[16px]"
                      style={{ color: "#09077D" }}
                    >
                      IDA • {dataIda}
                    </p>
                  </div>
                </div>
              </motion.button>

              {/* Card VOLTA */}
              {voosVolta.length > 0 && (
                <motion.button
                  onClick={() => onNavigateToTimeline("volta")}
                  className="w-full bg-gradient-to-br from-purple-50 to-white rounded-[16px] p-5 shadow-md border border-purple-100"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.4 }}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                      style={{ background: "#7C3AED" }}
                    >
                      <Plane
                        className="w-6 h-6 text-white"
                        style={{ transform: "rotate(225deg)" }}
                      />
                    </div>
                    <div className="text-left">
                      <p
                        className="text-[16px]"
                        style={{ color: "#7C3AED" }}
                      >
                        VOLTA • {dataVolta}
                      </p>
                    </div>
                  </div>
                </motion.button>
              )}

              {/* Card Bagagem */}
              <motion.div
                className="rounded-[16px] p-5 shadow-md border border-green-100"
                style={{ background: "#50CFAD20" }}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.5 }}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                    style={{ background: "#50CFAD" }}
                  >
                    <svg
                      className="w-6 h-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div>
                    <p
                      className="text-[16px]"
                      style={{ color: "#059669" }}
                    >
                      1 mala despachada incluída
                    </p>
                  </div>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
