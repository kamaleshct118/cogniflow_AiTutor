/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Dark Reader Theme — Night Parchment & Neon Amber
        obsidian: '#121316',
        charcoal: {
          DEFAULT: '#1B1C22',
          light: '#25262E',
          border: '#2E2F38',
        },
        parchment: '#E8E5DF',
        amber: {
          DEFAULT: '#FFB020',
          glow: '#FFC940',
          dim: '#B87D18',
        },
        violet: {
          DEFAULT: '#8B5CF6',
          glow: '#A78BFA',
          dim: '#6D28D9',
        },
        terracotta: {
          DEFAULT: '#F97316',
          glow: '#FB923C',
          dim: '#C2410C',
        },
        mint: {
          DEFAULT: '#10B981',
          glow: '#34D399',
          dim: '#047857',
        },
        // Sepia Light Theme
        paper: '#FAF6F0',
        'aged-page': '#F3EDE2',
        'deep-ink': '#1C1917',
        cinnamon: '#D97706',
        indigo: {
          DEFAULT: '#6366F1',
          glow: '#818CF8',
        },
      },
      fontFamily: {
        serif: ['Lora', 'Newsreader', 'Georgia', 'serif'],
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Menlo', 'monospace'],
      },
      lineHeight: {
        relaxed: '1.7',
        tight: '1.2',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2.5s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'fade-in': 'fade-in 0.5s ease-out',
        'slide-up': 'slide-up 0.4s ease-out',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '1', filter: 'brightness(1)' },
          '50%': { opacity: '0.8', filter: 'brightness(1.3)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      backgroundImage: {
        'groovy-gradient': 'linear-gradient(135deg, #FFB020 0%, #F97316 50%, #8B5CF6 100%)',
        'neural-grid': 'radial-gradient(circle at 1px 1px, rgba(255,176,32,0.08) 1px, transparent 0)',
      },
    },
  },
  plugins: [],
};
