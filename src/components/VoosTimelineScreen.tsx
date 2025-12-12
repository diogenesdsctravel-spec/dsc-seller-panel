import { Plane, MapPin, Clock, ChevronLeft } from "lucide-react";
import { motion } from "framer-motion";
import { countryCodeToFlag } from "../utils/countryCodeToFlag";

interface VoosTimelineScreenProps {
  tripData: any;
  tipo: "ida" | "volta";
  onBack: () => void;
  onNavigateToVolta?: () => void;
  onTabChange?: (tab: string) => void;
}

type AeroportoTimeline = {
  codigo: string;
  cidade: string;
  chegada: string | null;
  partida: string | null;
};

function parseHoraToMinutos(hora: string | undefined): number | null {
  if (!hora) return null;
  const [h, m] = hora.split(":").map((v) => parseInt(v, 10));
  if (Number.isNaN(h) || Number.isNaN(m)) return null;
  return h * 60 + m;
}

function calcularDuracaoConexao(
  horaChegada: string | null,
  horaSaida: string | null
): string | null {
  if (!horaChegada || !horaSaida) return null;

  const chegadaMin = parseHoraToMinutos(horaChegada);
  const saidaMin = parseHoraToMinutos(horaSaida);
  if (chegadaMin === null || saidaMin === null) return null;

  let diff = saidaMin - chegadaMin;
  if (diff < 0) diff += 24 * 60;

  const horas = Math.floor(diff / 60);
  const minutos = diff % 60;

  if (horas <= 0 && minutos <= 0) return null;

  const horasStr = horas > 0 ? `${horas}h` : "";
  const minutosStr =
    minutos > 0 ? `${minutos.toString().padStart(2, "0")}m` : "";

  if (horasStr && minutosStr) return `${horasStr}${minutosStr}`;
  if (horasStr) return horasStr;
  return minutosStr;
}

export function VoosTimelineScreen({
  tripData,
  tipo,
  onBack,
  onNavigateToVolta,
}: VoosTimelineScreenProps) {
  const cliente = tripData?.cliente || "Cliente";
  const voos = tripData?.voos || [];
  const imagemHero =
    tripData?.imagem_hero ||
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80";
  const imagensCidades = tripData?.imagens_cidades || {};

  const countryCodes: string[] = tripData?.paises?.length
    ? tripData.paises
    : ["BR"];
  const bandeiras = countryCodes.map(countryCodeToFlag);

  const todosVoos = [...voos];
  const metade = Math.ceil(todosVoos.length / 2);
  const voosIda = todosVoos.slice(0, metade);
  const voosVolta = todosVoos.slice(metade);

  const voosExibir = tipo === "ida" ? voosIda : voosVolta;
  const dataVolta = voosVolta[0]?.data || "Data";

  const aeroportos: AeroportoTimeline[] = [];

  if (voosExibir.length > 0) {
    const primeiroVoo = voosExibir[0];

    const origemCidade =
      primeiroVoo.origem?.split("(")[0]?.trim() || "Origem";
    const origemCodigo =
      primeiroVoo.origem?.match(/\(([^)]+)\)/)?.[1] || primeiroVoo.origem || "";

    aeroportos.push({
      codigo: origemCodigo,
      cidade: origemCidade,
      chegada: null,
      partida: primeiroVoo.horario_saida || null,
    });

    voosExibir.forEach((voo: any, idx: number) => {
      const destinoCidade =
        voo.destino?.split("(")[0]?.trim() || "Destino";
      const destinoCodigo =
        voo.destino?.match(/\(([^)]+)\)/)?.[1] || voo.destino || "";

      const isUltimoVoo = idx === voosExibir.length - 1;
      const proximoVoo = !isUltimoVoo ? voosExibir[idx + 1] : null;

      aeroportos.push({
        codigo: destinoCodigo,
        cidade: destinoCidade,
        chegada: voo.horario_chegada || null,
        partida: proximoVoo?.horario_saida || null,
      });
    });
  }

  return (
    <div className="absolute inset-0 flex flex-col bg-white">
      <div className="flex-1 overflow-y-auto">
        <div className="px-6 pt-16 pb-8">
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
            <div
              className="rounded-[16px] p-4 mb-6 shadow-lg"
              style={{ background: "#09077D" }}
            >
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-full bg-green-400 flex items-center justify-center">
                  <svg
                    className="w-3 h-3 text-white"
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
                <p className="text-white text-[15px]">
                  Selecionado para {cliente}
                </p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-[16px] p-4 mb-6 flex items-center justify-between shadow-sm">
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-gray-500" />
                <div>
                  <p className="text-[11px] text-gray-500">Duração</p>
                  <p className="text-[14px]" style={{ color: "#09077D" }}>
                    {tipo === "ida" ? "Viagem de ida" : "Viagem de volta"}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 flex items-center justify-center">
                    <svg
                      className="w-5 h-5 text-gray-500"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="text-[11px] text-gray-500">Classe</p>
                    <p
                      className="text-[14px]"
                      style={{ color: "#09077D" }}
                    >
                      Econômica
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-1">
                  {bandeiras.map((flag, idx) => (
                    <span
                      key={idx}
                      className="text-[18px] leading-none"
                    >
                      {flag}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="relative pb-6">
              <div
                className="absolute left-[20px] top-[24px] w-[3px] bg-gradient-to-b from-blue-400 via-blue-300 to-blue-400"
                style={{ height: "calc(100% - 80px)" }}
              />

              {aeroportos.map((ap, index) => {
                const isPrimeiro = index === 0;
                const isUltimo = index === aeroportos.length - 1;

                const Icon = isPrimeiro || !isUltimo ? Plane : MapPin;
                const iconStyle = isUltimo ? "#50CFAD" : "#09077D";

                const mostrarChegada = !isPrimeiro && ap.chegada;
                const mostrarPartida = !isUltimo && ap.partida;

                const proximo = aeroportos[index + 1];
                const duracaoConexao =
                  proximo && proximo.chegada && proximo.partida
                    ? calcularDuracaoConexao(
                      proximo.chegada,
                      proximo.partida
                    )
                    : null;

                const imagemCidade =
                  imagensCidades[ap.cidade] ||
                  imagensCidades[ap.codigo] ||
                  imagemHero;

                return (
                  <div key={index}>
                    <motion.div
                      className="relative mb-6"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{
                        duration: 0.5,
                        delay: 0.2 + index * 0.1,
                      }}
                    >
                      <div className="flex gap-4">
                        <div
                          className="relative z-10 w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                          style={{ background: iconStyle }}
                        >
                          <Icon
                            className="w-5 h-5 text-white"
                            style={
                              Icon === Plane
                                ? { transform: "rotate(45deg)" }
                                : undefined
                            }
                          />
                        </div>

                        <div className="flex-1 bg-white rounded-[16px] p-4 shadow-md border border-gray-100">
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex-1">
                              <p
                                className="text-[18px] mb-1"
                                style={{ color: "#09077D" }}
                              >
                                {ap.codigo}
                              </p>
                              <p className="text-[14px] text-gray-600 mb-2">
                                {ap.cidade}
                              </p>

                              {isPrimeiro && ap.partida && (
                                <p
                                  className="text-[15px]"
                                  style={{ color: "#6B7280" }}
                                >
                                  Partida:{" "}
                                  <span style={{ color: "#09077D" }}>
                                    {ap.partida}
                                  </span>
                                </p>
                              )}

                              {!isPrimeiro && !isUltimo && (
                                <>
                                  {mostrarChegada && (
                                    <p
                                      className="text-[15px] mb-1"
                                      style={{ color: "#6B7280" }}
                                    >
                                      Chegada:{" "}
                                      <span
                                        style={{ color: "#09077D" }}
                                      >
                                        {ap.chegada}
                                      </span>
                                    </p>
                                  )}
                                  {mostrarPartida && (
                                    <p
                                      className="text-[15px]"
                                      style={{ color: "#6B7280" }}
                                    >
                                      Partida:{" "}
                                      <span
                                        style={{ color: "#09077D" }}
                                      >
                                        {ap.partida}
                                      </span>
                                    </p>
                                  )}
                                </>
                              )}

                              {isUltimo && mostrarChegada && (
                                <p
                                  className="text-[15px]"
                                  style={{ color: "#6B7280" }}
                                >
                                  Chegada:{" "}
                                  <span style={{ color: "#09077D" }}>
                                    {ap.chegada}
                                  </span>
                                </p>
                              )}
                            </div>

                            <div className="w-16 h-16 rounded-[14px] overflow-hidden flex-shrink-0">
                              <img
                                src={imagemCidade}
                                alt={ap.cidade}
                                className="w-full h-full object-cover"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </motion.div>

                    {proximo && duracaoConexao && (
                      <div className="ml-[52px] mb-4">
                        <div className="flex items-center gap-2 text-[13px] text-gray-500">
                          <Clock className="w-4 h-4" />
                          <span>Conexão: {duracaoConexao}</span>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {tipo === "ida" &&
              voosVolta.length > 0 &&
              onNavigateToVolta && (
                <motion.button
                  onClick={onNavigateToVolta}
                  className="w-full bg-gradient-to-br from-purple-50 to-white rounded-[16px] p-5 shadow-md border border-purple-100 mt-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.6 }}
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
          </motion.div>
        </div>
      </div>
    </div>
  );
}
