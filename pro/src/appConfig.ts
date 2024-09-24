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
    }
  }
}

// export let appConfig: Config

export async function loadConfig() {
  const root = document.documentElement
  await import(
    `../configs/${import.meta.env.VITE_APP_CONFIG ?? process.env.VITE_APP_CONFIG}.json`
  )
    .then((config: Config) => {
      // appConfig = config
      root.style.setProperty('--color-primary', config.ui.colors.primary)
      root.style.setProperty('--color-secondary', config.ui.colors.secondary)
    })
    .catch(() => {
      // Error happend
    })
}
