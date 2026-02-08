// Color Palette Configuration
// Customize these hex values to change the entire app's color scheme

export const colors = {
  // Primary Brand Colors
  primary: {
    main:    '#0A1F40',  // keep
    hover:   '#071936',  // remove alpha, slightly darker
    light:   '#143664',  // slightly brighter, clearer step up
    dark:    '#020F29',  // slightly deeper, closer to header
  },

  // Anomaly Severity Colors (darker, richer tones)
  severity: {
    severe:   '#DC2626', // darker red
    new:      '#EA580C', // deeper orange
    existing: '#CA8A04', // darker amber/yellow
    none:     '#4B5563', // mid gray for dark UI
  },

  // Confidence Level Colors (richer, tuned for dark)
  confidence: {
    high:   '#22C55E', // brighter green for clarity
    medium: '#3B82F6', // keep, works well on dark
    low:    '#9CA3AF', // lighter gray so it’s visible on dark bg
  },

  // Background Colors (unify around dark slate/blue)
  background: {
    page:     '#0B1120', // deeper, more “night mode”
    card:     '#111827', // slight elevation over page
    header:   '#020617', // very dark, still on-brand
    hover:    '#1F2933', // subtle hover on dark
    selected: '#1E293B', // darker “selected” for dark theme
  },

  // Text Colors (tuned for dark backgrounds)
  text: {
    primary:   '#E5E7EB', // light gray for main text on dark
    secondary: '#9CA3AF', // softer secondary
    light:     '#6B7280', // muted/disabled
    white:     '#FFFFFF',
    link:      '#60A5FA', // lighter blue for readability
    linkHover: '#3B82F6',
  },

  // Status Colors (align with severity + confidence)
  status: {
    success: '#22C55E',
    warning: '#EAB308',
    error:   '#EF4444',
    info:    '#3B82F6',
  },

  // Border Colors (for dark surfaces)
  border: {
    light:  '#1F2933', // subtle separators on dark
    medium: '#4B5563',
    dark:   '#6B7280',
    focus:  '#60A5FA', // brighter for accessibility
  },

  // Button Colors
  button: {
    primary:       '#22C55E', // success green as main action
    primaryHover:  '#16A34A',
    secondary:     '#1E40AF', // deep blue secondary
    secondaryHover:'#1D4ED8',
    danger:        '#DC2626',
    dangerHover:   '#B91C1C',
    disabled:      '#4B5563',
  },

  // Test Mode
  test: {
    button:      '#EAB308',
    buttonHover: '#CA8A04',
    text:        '#1E293B',
  },
};

// Helper function to get color by path (e.g., 'primary.main')
export const getColor = (path) => {
  return path.split('.').reduce((obj, key) => obj?.[key], colors)
}

export default colors
