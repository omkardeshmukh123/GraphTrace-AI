/* Node type → aesthetic color, icon glyph and visual weight mapping */
export const NODE_COLORS: Record<string, string> = {
  PROJECT:     '#818cf8', // Indigo
  PACKAGE:     '#a78bfa', // Violet
  FILE:        '#38bdf8', // Sky
  CLASS:       '#34d399', // Emerald
  FUNCTION:    '#f472b6', // Pink
  METHOD:      '#fb923c', // Amber-Orange
  REQUIREMENT: '#f43f5e', // Rose
  DOCUMENT:    '#2dd4bf', // Teal
  TECHNOLOGY:  '#06b6d4', // Cyan
  MODULE:      '#a3e635', // Lime
  INTERFACE:   '#c084fc', // Purple
};

export const NODE_GLOWS: Record<string, string> = {
  PROJECT:     'rgba(129, 140, 248, 0.4)',
  PACKAGE:     'rgba(167, 139, 250, 0.35)',
  FILE:        'rgba(56, 189, 248, 0.35)',
  CLASS:       'rgba(52, 211, 153, 0.35)',
  FUNCTION:    'rgba(244, 114, 182, 0.35)',
  METHOD:      'rgba(251, 146, 60, 0.35)',
  REQUIREMENT: 'rgba(244, 63, 94, 0.45)',
  DOCUMENT:    'rgba(45, 212, 191, 0.35)',
  TECHNOLOGY:  'rgba(6, 182, 212, 0.35)',
  MODULE:      'rgba(163, 230, 53, 0.35)',
};

export const NODE_ICONS: Record<string, string> = {
  PROJECT:     '📦',
  PACKAGE:     '📁',
  FILE:        '📄',
  CLASS:       '🏛️',
  FUNCTION:    'ƒ',
  METHOD:      '⚙️',
  REQUIREMENT: '📋',
  DOCUMENT:    '📝',
  TECHNOLOGY:  '⚡',
  MODULE:      '🧩',
};

export const NODE_COLOR_DEFAULT = '#94a3b8';

export function nodeColor(type: string): string {
  return NODE_COLORS[type?.toUpperCase()] ?? NODE_COLOR_DEFAULT;
}

export function nodeGlow(type: string): string {
  return NODE_GLOWS[type?.toUpperCase()] ?? 'rgba(148, 163, 184, 0.25)';
}

export function nodeIcon(type: string): string {
  return NODE_ICONS[type?.toUpperCase()] ?? '●';
}

export const NODE_SIZES: Record<string, number> = {
  PROJECT:     12,
  REQUIREMENT: 9,
  PACKAGE:     8,
  CLASS:       7,
  FILE:        6,
  FUNCTION:    5,
  DOCUMENT:    5,
  METHOD:      4,
  TECHNOLOGY:  6,
  MODULE:      7,
};

export function nodeSize(type: string): number {
  return NODE_SIZES[type?.toUpperCase()] ?? 5;
}
