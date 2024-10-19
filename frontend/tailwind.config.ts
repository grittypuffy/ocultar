/** @type {import('tailwindcss').Config} */
import daisyui from "daisyui"

import type { Config } from 'tailwindcss';

const config: Config = {
   mode: 'jit',
    content: [
      'index.html',
      './src/**/*.{js,ts,jsx,tsx,mdx,html}',
    ],
    theme: {
    fontFamily: {
      montserrat: ["Montserrat", "sans-serif"],
      oswald: ["Oswald", "sans-serif"],
      sourcesans: ["Source Sans", "sans-serif"],
      'sans': ["Source Sans", "Montserrat", 'system-ui'],
      'serif': ['ui-serif'],
      'mono': ['ui-monospace'],
      'display': ["Source Sans"],
      'body': ["Source Sans"]
    },
    extend: {
      fontFamily: {
        regular: ["Oswald"]
      },
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
  daisyui: {
    themes: ["corporate", "light", "dark", "cupcake", "pastel"],
    darkTheme: "dark", // name of one of the included themes for dark mode
    base: true, // applies background color and foreground color for root element by default
    styled: true, // include daisyUI colors and design decisions for all components
    utils: true, // adds responsive and modifier utility classes
    prefix: "", // prefix for daisyUI classnames (components, modifiers and responsive class names. Not colors)
    logs: true, // Shows info about daisyUI version and used config in the console when building your CSS
    themeRoot: ":root", // Th
  }
};

export default config;