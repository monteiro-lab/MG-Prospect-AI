/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                mg: {
                    // Backgrounds
                    bg: '#08090B',
                    bgalt: '#090A0D',
                    surface: '#111318',
                    elevated: '#17191F',
                    high: '#1D2027',

                    // Borders
                    border: 'rgba(197, 160, 89, 0.18)',
                    bordersub: 'rgba(197, 160, 89, 0.10)',
                    borderbold: 'rgba(197, 160, 89, 0.30)',

                    // Gold palette
                    gold: '#C9A24D',
                    goldlight: '#E4C978',
                    golddark: '#8A6A2F',
                    goldmuted: 'rgba(201, 162, 77, 0.15)',

                    // Text
                    text: '#F5F2EA',
                    sub: '#B8B8B8',
                    muted: '#7E818A',

                    // Status
                    success: '#36C98A',
                    error: '#E05D5D',
                    warning: '#E4B64A',
                    info: '#69A7FF',
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
            },
            fontSize: {
                '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
            },
            boxShadow: {
                'premium': '0 4px 24px rgba(0, 0, 0, 0.4)',
                'premium-lg': '0 8px 40px rgba(0, 0, 0, 0.5)',
                'glow': '0 0 20px rgba(201, 162, 77, 0.15)',
                'glowlg': '0 0 40px rgba(201, 162, 77, 0.20)',
                'card': '0 1px 3px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2)',
                'cardhover': '0 4px 16px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(201, 162, 77, 0.15)',
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gold-gradient': 'linear-gradient(135deg, #C9A24D 0%, #E4C978 50%, #C9A24D 100%)',
                'gold-subtle': 'linear-gradient(135deg, rgba(201,162,77,0.1) 0%, rgba(228,201,120,0.05) 100%)',
            },
            animation: {
                'slide-in-right': 'slide-in-right 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards',
                'fade-in': 'fade-in 0.2s ease-out forwards',
                'fade-in-up': 'fade-in-up 0.3s ease-out forwards',
            },
            keyframes: {
                'slide-in-right': {
                    from: { transform: 'translateX(100%)' },
                    to: { transform: 'translateX(0)' },
                },
                'fade-in': {
                    from: { opacity: '0' },
                    to: { opacity: '1' },
                },
                'fade-in-up': {
                    from: { opacity: '0', transform: 'translateY(8px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
            },
            spacing: {
                '18': '4.5rem',
                '88': '22rem',
            },
        },
    },
    plugins: [],
}