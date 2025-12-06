import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { DollarSign } from "lucide-react";
import { TripData } from "../types/trip";

interface BudgetSectionProps {
    data: TripData;
}

export function BudgetSection({ data }: BudgetSectionProps) {
    const hasBudget = data.pacote_base || (data.passeios && data.passeios.length > 0);

    if (!hasBudget) {
        return null;
    }

    return (
        <Card className="shadow-[0_18px_45px_rgba(15,23,42,0.08)]">
            <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-gray-700" />
                    <CardTitle className="text-lg font-normal">Orçamento</CardTitle>
                </div>
            </CardHeader>
            <CardContent className="space-y-6">
                {/* Pacote Base */}
                {data.pacote_base && (
                    <div>
                        <h3 className="text-sm font-semibold text-gray-700 mb-3">Incluso</h3>
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-sm font-medium text-gray-900">
                                        {data.pacote_base.descricao}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">Valor total para o casal</p>
                                </div>
                                <p className="text-lg font-semibold text-green-700">
                                    R$ {data.pacote_base.valor.toLocaleString('pt-BR')}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Opcionais */}
                {data.passeios && data.passeios.length > 0 && (
                    <div>
                        <h3 className="text-sm font-semibold text-gray-700 mb-3">Opcionais</h3>
                        <div className="space-y-2">
                            {data.passeios.map((passeio, index) => (
                                <div
                                    key={index}
                                    className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg"
                                >
                                    <p className="text-sm text-gray-700">{passeio.nome}</p>
                                    <div className="text-right">
                                        <p className="text-sm font-medium text-gray-900">
                                            R$ {passeio.valor_por_pessoa.toFixed(2)}
                                        </p>
                                        <p className="text-xs text-gray-500">por pessoa</p>
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