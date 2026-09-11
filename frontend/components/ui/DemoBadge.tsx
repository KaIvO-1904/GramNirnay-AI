import React from 'react';
import { Badge } from './badge';
import { Beaker } from 'lucide-react';

interface DemoBadgeProps {
  visible: boolean;
}

export const DemoBadge: React.FC<DemoBadgeProps> = ({ visible }) => {
  if (!visible) return null;

  return (
    <Badge
      variant="outline"
      className="bg-amber-50 text-amber-700 border-amber-200 flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider"
    >
      <Beaker className="w-3 h-3" />
      SIH Demo Mode: Synthetic Data
    </Badge>
  );
};
