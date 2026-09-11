/* Node type → colour mapping (mirrors CSS tokens) */
export const NODE_COLORS: Record<string, string> = {
  PROJECT:     '#818cf8',
  FILE:        '#60a5fa',
  PACKAGE:     '#a78bfa',
  CLASS:       '#34d399',
  FUNCTION:    '#f472b6',
  METHOD:      '#fb923c',
  REQUIREMENT: '#fbbf24',
  DOCUMENT:    '#94a3b8',
  TECHNOLOGY:  '#22d3ee',
  MODULE:      '#a3e635',
  INTERFACE:   '#f9a8d4',
};

export const NODE_COLOR_DEFAULT = '#64748b';

export function nodeColor(type: string): string {
  return NODE_COLORS[type?.toUpperCase()] ?? NODE_COLOR_DEFAULT;
}

export const NODE_SIZES: Record<string, number> = {
  PROJECT:  10,
  PACKAGE:   7,
  FILE:      6,
  CLASS:     6,
  FUNCTION:  5,
  METHOD:    4,
  REQUIREMENT: 8,
  DOCUMENT:  5,
  TECHNOLOGY: 6,
};

export function nodeSize(type: string): number {
  return NODE_SIZES[type?.toUpperCase()] ?? 5;
}
