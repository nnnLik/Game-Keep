export const TABS = [
  { id: 'backlog', label: 'В планах', icon: 'lucide:cloud', colorKey: 'slate' },
  { id: 'in_progress', label: 'Играю', icon: 'lucide:gamepad-2', colorKey: 'emerald' },
  { id: 'completed', label: 'Пройдено', icon: 'lucide:flag', colorKey: 'teal' },
  { id: 'abandoned', label: 'Брошено', icon: 'lucide:x-circle', colorKey: 'amber' },
  { id: 'favorites', label: 'Избранное', icon: 'lucide:heart', colorKey: 'rose' },
] as const

export const TAB_ACTIVE_CLASSES: Record<string, string> = {
  slate: 'border-slate-500/70 text-slate-300',
  emerald: 'border-emerald-500/70 text-emerald-200',
  teal: 'border-teal-500/70 text-teal-200',
  amber: 'border-amber-500/70 text-amber-200',
  rose: 'border-rose-500/70 text-rose-200',
}
export const TAB_ICON_CLASSES: Record<string, string> = {
  slate: 'text-slate-400',
  emerald: 'text-emerald-400',
  teal: 'text-teal-400',
  amber: 'text-amber-400',
  rose: 'text-rose-400',
}
export const TAB_BADGE_CLASSES: Record<string, string> = {
  slate: 'bg-slate-500/25 text-slate-300',
  emerald: 'bg-emerald-500/25 text-emerald-300',
  teal: 'bg-teal-500/25 text-teal-300',
  amber: 'bg-amber-500/25 text-amber-300',
  rose: 'bg-rose-500/25 text-rose-300',
}
