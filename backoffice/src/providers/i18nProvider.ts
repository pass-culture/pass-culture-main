import polyglotI18nProvider from 'ra-i18n-polyglot'

import frenchMessages from '../i18n/fr'

export enum LOCALES {
  EN = 'en',
  FR = 'fr',
}

export const initialLocale = LOCALES.FR

export const i18nProvider = polyglotI18nProvider(
  locale => {
    if (locale === LOCALES.EN) {
      return import('../i18n/en').then(messages => messages.default) // for later
    }
    // initial call, must return synchronously
    return frenchMessages
  },
  initialLocale,
  {
    allowMissing: true,
  }
)
