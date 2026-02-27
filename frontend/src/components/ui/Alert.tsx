import React from 'react';
import { cn } from '@/lib/utils';
import { AlertCircle, AlertTriangle, Info } from 'lucide-react';

type AlertType = 'danger' | 'warning' | 'info';

interface AlertProps {
  type?: AlertType;
  title?: string;
  children: React.ReactNode;
  className?: string;
}

const alertStyles: Record<AlertType, string> = {
  danger: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
};

const alertIcons: Record<AlertType, React.ReactNode> = {
  danger: <AlertCircle className="w-5 h-5 text-red-600" />,
  warning: <AlertTriangle className="w-5 h-5 text-yellow-600" />,
  info: <Info className="w-5 h-5 text-blue-600" />,
};

export function Alert({ type = 'info', title, children, className }: AlertProps) {
  return (
    <div className={cn(
      'rounded-lg border p-4 flex gap-3',
      alertStyles[type],
      className
    )}>
      <div className="flex-shrink-0">
        {alertIcons[type]}
      </div>
      <div className="flex-1">
        {title && (
          <h4 className="font-semibold mb-1">{title}</h4>
        )}
        <div className="text-sm">{children}</div>
      </div>
    </div>
  );
}
