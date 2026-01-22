// src/plugins/vuetify.js
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

const cabinetTheme = {
  dark: false,
  colors: {
    primary: '#1A237E',     // Bleu Indigo profond
    secondary: '#FFD700',   // Or Gabon
    accent: '#FF6D00',
    background: '#F5F5F5',
    surface: '#FFFFFF',
    error: '#D32F2F',
    info: '#1976D2',
    success: '#388E3C',
    warning: '#F57C00',
  }
}

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi }
  },
  theme: {
    defaultTheme: 'cabinetTheme',
    themes: {
      cabinetTheme
    }
  }
})