import { Home, Calendar, Grid3x3, DollarSign, User } from 'lucide-react';

interface BottomNavigationProps {
    activeTab?: 'inicio' | 'roteiro' | 'produtos' | 'orcamento' | 'conta';
    onTabChange?: (tab: string) => void;
}

export function BottomNavigation({ activeTab = 'inicio', onTabChange }: BottomNavigationProps) {
    const tabs = [
        { id: 'inicio', label: 'Início', icon: Home },
        { id: 'roteiro', label: 'Roteiro', icon: Calendar },
        { id: 'produtos', label: 'Produtos', icon: Grid3x3 },
        { id: 'orcamento', label: 'Orçamento', icon: DollarSign },
        { id: 'conta', label: 'Conta', icon: User },
    ];

    return (
        <div
            className="bg-white border-t border-gray-200"
            style={{ paddingBottom: 'max(env(safe-area-inset-bottom), 8px)' }}
        >
            <div className="flex items-center justify-around px-2 py-2">
                {tabs.map((tab) => {
                    const Icon = tab.icon;
                    const isActive = activeTab === tab.id;

                    return (
                        <button
                            key={tab.id}
                            onClick={() => onTabChange?.(tab.id)}
                            className="flex flex-col items-center justify-center min-w-[64px] py-1 transition-colors"
                        >
                            <Icon
                                className="w-6 h-6 mb-1"
                                style={{
                                    color: isActive ? '#09077D' : '#9CA3AF',
                                    strokeWidth: isActive ? 2.5 : 2
                                }}
                            />
                            <span
                                className="text-[11px]"
                                style={{
                                    color: isActive ? '#09077D' : '#9CA3AF',
                                    fontWeight: isActive ? '600' : '400'
                                }}
                            >
                                {tab.label}
                            </span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}