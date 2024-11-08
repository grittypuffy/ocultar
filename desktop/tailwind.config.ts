/** @type {import('tailwindcss').Config} */
import daisyui from "daisyui"

import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    'index.html',
    './src/**/*.{js,ts,jsx,tsx,mdx,html}',
  ],
  theme: {
    extend: {
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':
          'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [
    daisyui
  ],
};

export default config;