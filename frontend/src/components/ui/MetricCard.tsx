import React from 'react';
import { cn, formatCurrency, formatPercentage } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  change?: number;
  changeLabel?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
  isCurrency?: boolean;
  isPercentage?: boolean;
  className?: string;
}

export function MetricCard({
  title,
  value,
  subtitle,
  change,
  changeLabel,
  trend = 'neutral',
  icon,
  isCurrency = false,
  isPercentage = false,
  className,
}: MetricCardProps) {
  const formattedValue = isCurrency
    ? formatCurrency(typeof value === 'number' ? value : 0)
    : isPercentage
    ? formatPercentage(typeof value === 'number' ? value : 0)
    : value;

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  const trendColor = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-500';

  return (
    <div className={cn('bg-white rounded-lg border border-gray-200 p-6', className)}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{formattedValue}</p>
          
          {subtitle && (
            <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
          )}
          
          {change !== undefined && (
            <div className="mt-4 flex items-center gap-2">
              <TrendIcon className={cn('w-4 h-4', trendColor)} />
              <span className={cn('text-sm font-medium', trendColor)}>
                {change > 0 ? '+' : ''}{change.toFixed(1)}%
              </span>
              {changeLabel && (
                <span className="text-sm text-gray-500">{changeLabel}</span>
              )}
            </div>
          )}
        </div>
        
        {icon && (
          <div className="p-3 bg-gray-100 rounded-lg">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
