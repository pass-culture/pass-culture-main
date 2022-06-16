import polyglotI18nProvider from 'ra-i18n-polyglot'

import englishMessages from '../i18n/en'

export enum LOCALES {
  EN = 'en',
  FR = 'fr',
}

export const initialLocale = LOCALES.EN

export const i18nProvider = polyglotI18nProvider(locale => {
  if (locale === LOCALES.FR) {
    return import('../i18n/fr').then(messages => messages.default) // for later
  }
  // initial call, must return synchronously
  return englishMessages
}, initialLocale)
