import { FunctionComponent } from 'react'

import FrenchLogo from 'components/Logos/FrenchLogo'

interface Config {
  name: string
  languages: {
    supportedLngs: string[]
    fallbackLng: string
  }
  ui: {
    logo: string
    colors: {
      primary: string
      secondary: string
      secondaryLighter: string
      secondaryLight: string
      secondaryDark: string
      primaryDark: string
      backgroundSecondary: string
      backgroundAccentLight: string
    }
  }
}

export let appConfig: Config
export let AppLogo: FunctionComponent<any> = FrenchLogo

export async function loadConfig() {
  const root = document.documentElement
  await import(
    `../configs/${import.meta.env.VITE_APP_CONFIG ?? process.env.VITE_APP_CONFIG}.json`
  )
    .then(async (config: Config) => {
      appConfig = config
      AppLogo = (await import(`./components/Logos/${config.ui.logo}.tsx`))
        .default

      root.style.setProperty('--color-primary', config.ui.colors.primary)
      root.style.setProperty('--color-secondary', config.ui.colors.secondary)
      root.style.setProperty(
        '--color-secondary-lighter',
        config.ui.colors.secondaryLighter
      )
      root.style.setProperty(
        '--color-secondary-light',
        config.ui.colors.secondaryLight
      )
      root.style.setProperty(
        '--color-secondary-dark',
        config.ui.colors.secondaryDark
      )
      root.style.setProperty(
        '--color-primary-dark',
        config.ui.colors.primaryDark
      )
      root.style.setProperty(
        '--color-background-secondary',
        config.ui.colors.backgroundSecondary
      )
      root.style.setProperty(
        '--color-background-accent-light',
        config.ui.colors.backgroundAccentLight
      )
    })
    .catch(() => {
      // Error happend
    })
}
