import React from "react";

type ProdutosScreenProps = {
  tripData?: any;
  onNavigate: (
    screen:
      | "hero"
      | "cidades"
      | "roteiro"
      | "produtos"
      | "voos"
      | "hoteis"
      | "transfers"
      | "passeios"
  ) => void;
  onTabChange?: (
    tab: "inicio" | "roteiro" | "produtos" | "orcamento" | "conta"
  ) => void; // mantido só para compatibilidade
};

export function ProdutosScreen({
  tripData,
  onNavigate,
}: ProdutosScreenProps) {
  const voos = tripData?.voos || [];
  const hoteis = tripData?.hoteis || [];
  const transfers = tripData?.transfers || [];
  const passeios = tripData?.passeios || [];

  const voosTexto =
    voos.length === 0
      ? "Nenhum voo incluído"
      : `${voos.length} trecho${voos.length > 1 ? "s" : ""} incluído${voos.length > 1 ? "s" : ""
      }`;

  const hoteisTexto =
    hoteis.length === 0
      ? "Nenhum hotel incluído"
      : `${hoteis.length} hotel${hoteis.length > 1 ? "es" : ""
      } • ${hoteis.reduce(
        (sum: number, h: any) => sum + (h.noites || 0),
        0
      ) || 0
      } noites`;

  const transfersTexto =
    transfers.length === 0
      ? "Aeroporto e hotel (a definir)"
      : `${transfers.length} transfer${transfers.length > 1 ? "s" : ""
      } incluído${transfers.length > 1 ? "s" : ""}`;

  const passeiosTexto =
    passeios.length === 0
      ? "Tours e experiências selecionadas"
      : `${passeios.length} passeio${passeios.length > 1 ? "s" : ""
      } incluído${passeios.length > 1 ? "s" : ""}`;

  return (
    <div className="px-6 pt-16 pb-[120px]">
      <h1
        className="text-[32px] mb-3 leading-[1.1]"
        style={{ color: "#09077D", letterSpacing: "-0.02em" }}
      >
        Produtos
      </h1>
      <p className="text-[16px] leading-[1.5] text-gray-700 mb-10">
        Todos os serviços da sua viagem
      </p>

      <div className="space-y-4">
        {/* Voos */}
        <button
          type="button"
          onClick={() => onNavigate("voos")}
          className="w-full text-left"
        >
          <div className="flex items-center gap-4 bg-white rounded-[24px] px-5 py-5 shadow-[0_8px_20px_rgba(0,0,0,0.06)]">
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 text-[24px]"
              style={{ background: "#50CFAD", color: "white" }}
            >
              ✈️
            </div>
            <div className="flex-1">
              <p
                className="text-[18px] font-semibold mb-1"
                style={{ color: "#09077D" }}
              >
                Voos
              </p>
              <p className="text-[14px] text-gray-600">{voosTexto}</p>
            </div>
            <span className="text-[22px] text-gray-300">›</span>
          </div>
        </button>

        {/* Hotéis */}
        <button
          type="button"
          onClick={() => onNavigate("hoteis")}
          className="w-full text-left"
        >
          <div className="flex items-center gap-4 bg-white rounded-[24px] px-5 py-5 shadow-[0_8px_20px_rgba(0,0,0,0.06)]">
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 text-[24px]"
              style={{ background: "#50CFAD", color: "white" }}
            >
              🏨
            </div>
            <div className="flex-1">
              <p
                className="text-[18px] font-semibold mb-1"
                style={{ color: "#09077D" }}
              >
                Hotéis
              </p>
              <p className="text-[14px] text-gray-600">{hoteisTexto}</p>
            </div>
            <span className="text-[22px] text-gray-300">›</span>
          </div>
        </button>

        {/* Transfers */}
        <button
          type="button"
          onClick={() => onNavigate("transfers")}
          className="w-full text-left"
        >
          <div className="flex items-center gap-4 bg-white rounded-[24px] px-5 py-5 shadow-[0_8px_20px_rgba(0,0,0,0.06)]">
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 text-[24px]"
              style={{ background: "#50CFAD", color: "white" }}
            >
              🚐
            </div>
            <div className="flex-1">
              <p
                className="text-[18px] font-semibold mb-1"
                style={{ color: "#09077D" }}
              >
                Transfers
              </p>
              <p className="text-[14px] text-gray-600">
                {transfersTexto}
              </p>
            </div>
            <span className="text-[22px] text-gray-300">›</span>
          </div>
        </button>

        {/* Passeios */}
        <button
          type="button"
          onClick={() => onNavigate("passeios")}
          className="w-full text-left"
        >
          <div className="flex items-center gap-4 bg-white rounded-[24px] px-5 py-5 shadow-[0_8px_20px_rgba(0,0,0,0.06)]">
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 text-[24px]"
              style={{ background: "#50CFAD", color: "white" }}
            >
              🌿
            </div>
            <div className="flex-1">
              <p
                className="text-[18px] font-semibold mb-1"
                style={{ color: "#09077D" }}
              >
                Passeios
              </p>
              <p className="text-[14px] text-gray-600">
                {passeiosTexto}
              </p>
            </div>
            <span className="text-[22px] text-gray-300">›</span>
          </div>
        </button>
      </div>
    </div>
  );
}
