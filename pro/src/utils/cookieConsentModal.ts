import * as Orejime from 'orejime'
import { v4 as uuidv4 } from 'uuid'

import { api } from 'apiClient/api'
import { toISOStringWithoutMilliseconds } from 'utils/date'

export const initCookieConsent = () => {
  const mandatoryCookies = ['sentry']

  const orejimeConfig = {
    appElement: '#root',
    cookieExpiresAfterDays: 182,
    privacyPolicy: 'https://pass.culture.fr/politique-de-cookies/',
    default: false,
    debug: false,
    lang: 'fr',
    // This is called before saving the cookie.
    // We use it to execute the api call used to log the user consents
    // Still, we do not change the cookie content
    stringifyCookie: (contents: any) => {
      const nonMandatoryConsents = Object.entries(contents).filter(([app]) => {
        return mandatoryCookies.indexOf(app) === -1
      })
      const cookieConsent = {
        choiceDatetime: toISOStringWithoutMilliseconds(new Date()),
        consent: {
          accepted: nonMandatoryConsents
            .filter(([, consented]) => {
              return consented
            })
            .map(([app]) => {
              return app
            }),
          mandatory: Object.entries(contents)
            .filter(([app]) => {
              return mandatoryCookies.indexOf(app) >= 0
            })
            .map(([app]) => {
              return app
            }),
          refused: nonMandatoryConsents
            .filter(([, consented]) => {
              return !consented
            })
            .map(([app]) => {
              return app
            }),
        },
        deviceId: localStorage.getItem('DEVICE_ID') ?? '',
      }

      api.cookiesConsent(cookieConsent).then()

      return JSON.stringify(contents)
    },
    parseCookie: (cookie: string) => {
      return JSON.parse(cookie)
    },

    translations: {
      fr: {
        purposes: {
          needed: 'Essentiel',
          personalization: 'Personnalisation',
          perfs: 'Performance',
          market: 'Marketing',
        },
        firebase: {
          description:
            'Suivre les actions des utilisateurs afin d’améliorer leurs parcours et faciliter leur expérience. Mettre à jour facilement les codes de suivi et les balises afin de mesurer et analyser le comportement des utilisateurs. Collecter et analyser les données des utilisateurs.',
        },
        hotjar: {
          description:
            'Analyser les comportements des utilisateurs afin d’identifier les points de friction',
        },
        sentry: {
          description: 'Analyser les erreurs pour aider au débogguage',
        },
        beamer: {
          description:
            'Informer les utilisateurs des dernières nouveautés et fonctionnalités grâce à un centre de notifications',
        },
      },
    },

    apps: [
      {
        name: 'firebase',
        title: 'Firebase',
        cookies: /_ga.*/,
        purposes: ['personalization'],
      },
      {
        name: 'hotjar',
        title: 'Hotjar',
        cookies: /_hs.*/,
        purposes: ['perfs'],
      },
      {
        name: 'beamer',
        title: 'Beamer',
        purposes: ['market'],
        cookies: /_BEAMER.*/,
      },
      {
        name: 'sentry',
        title: 'Sentry',
        purposes: ['needed'],
        cookies: ['sentrysid'],
        required: true,
        default: true,
      },
    ],
    categories: [
      {
        name: 'needed',
        title: 'Essentiel',
        apps: ['sentry'],
      },
      {
        name: 'personalization',
        title: 'Personnalisation',
        apps: ['firebase'],
      },
      {
        name: 'perfs',
        title: 'Performance',
        apps: ['hotjar'],
      },
      {
        name: 'market',
        title: 'Marketing',

        apps: ['beamer'],
      },
    ],
  }

  setTimeout(() => {
    Orejime.init(orejimeConfig)
    if (localStorage.getItem('DEVICE_ID') == null) {
      localStorage.setItem('DEVICE_ID', uuidv4())
    }
  })
}
