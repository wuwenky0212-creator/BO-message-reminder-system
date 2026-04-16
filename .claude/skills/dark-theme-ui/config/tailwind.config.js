/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    './pages/**/*.{js,jsx,ts,tsx}',
    './components/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // 主题色
        primary: {
          DEFAULT: '#3b82f6',
          dark: '#2563eb',
          light: '#60a5fa',
        },
        
        // 背景色
        surface: {
          DEFAULT: '#1f1f1f',
          dark: '#1f1f1f',
          darker: '#1a1a1a',
          light: '#252525',
        },
        
        // 边框色
        border: {
          DEFAULT: '#374151',
          dark: '#374151',
          light: '#4b5563',
        },
        
        // 文字色
        text: {
          DEFAULT: '#e5e7eb',
          dark: '#e5e7eb',
          light: '#f3f4f6',
          muted: {
            DEFAULT: '#9ca3af',
            dark: '#9ca3af',
            light: '#d1d5db',
          },
        },
        
        // 状态色
        success: {
          DEFAULT: '#22c55e',
          dark: '#16a34a',
          light: '#4ade80',
        },
        error: {
          DEFAULT: '#ef4444',
          dark: '#dc2626',
          light: '#f87171',
        },
        warning: {
          DEFAULT: '#eab308',
          dark: '#ca8a04',
          light: '#facc15',
        },
        info: {
          DEFAULT: '#3b82f6',
          dark: '#2563eb',
          light: '#60a5fa',
        },
        
        // 特殊色
        accent: '#eab308',
        sidebar: '#001529',
        
        // 灰度色扩展
        gray: {
          850: '#1a1a1a',
          950: '#0a0a0a',
        },
      },
      
      // 阴影
      boxShadow: {
        'dark': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
        'dark-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
        'dark-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
      },
      
      // 动画
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      
      // 字体
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      
      // 间距
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      
      // 圆角
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
      },
      
      // 过渡
      transitionProperty: {
        'height': 'height',
        'spacing': 'margin, padding',
      },
    },
  },
  plugins: [
    // 自定义插件
    function({ addUtilities, addComponents, theme }) {
      // 添加自定义工具类
      addUtilities({
        '.scrollbar-dark': {
          '&::-webkit-scrollbar': {
            width: '6px',
            height: '6px',
          },
          '&::-webkit-scrollbar-track': {
            background: theme('colors.gray.800'),
          },
          '&::-webkit-scrollbar-thumb': {
            background: theme('colors.gray.600'),
            borderRadius: '3px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: theme('colors.gray.500'),
          },
        },
        '.focus-visible-ring': {
          '&:focus-visible': {
            outline: '2px solid transparent',
            outlineOffset: '2px',
            boxShadow: `0 0 0 2px ${theme('colors.primary.DEFAULT')}`,
          },
        },
      })
      
      // 添加组件样式
      addComponents({
        '.btn': {
          padding: `${theme('spacing.2')} ${theme('spacing.4')}`,
          borderRadius: theme('borderRadius.md'),
          fontWeight: theme('fontWeight.medium'),
          transition: 'all 0.2s ease-in-out',
          '&:focus': {
            outline: 'none',
            boxShadow: `0 0 0 2px ${theme('colors.primary.DEFAULT')}`,
          },
        },
        '.card': {
          backgroundColor: theme('colors.surface.dark'),
          borderRadius: theme('borderRadius.lg'),
          boxShadow: theme('boxShadow.dark'),
          border: `1px solid ${theme('colors.border.dark')}`,
        },
        '.input': {
          backgroundColor: '#141414',
          border: `1px solid ${theme('colors.border.dark')}`,
          borderRadius: theme('borderRadius.DEFAULT'),
          padding: `${theme('spacing.2')} ${theme('spacing.3')}`,
          color: theme('colors.text.dark'),
          fontSize: theme('fontSize.sm'),
          '&:focus': {
            outline: 'none',
            borderColor: theme('colors.primary.DEFAULT'),
          },
          '&::placeholder': {
            color: theme('colors.gray.600'),
          },
        },
      })
    },
  ],
}