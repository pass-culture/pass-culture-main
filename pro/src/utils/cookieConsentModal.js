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
    stringifyCookie: contents => {
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
        deviceId: localStorage.getItem('DEVICE_ID'),
      }

      api.cookiesConsent(cookieConsent).then()

      return JSON.stringify(contents)
    },
    parseCookie: cookie => {
      return JSON.parse(cookie)
    },

    translations: {
      fr: {
        purposes: {
          needed: 'Essentiel',
          personalization: 'Personnalisation',
          performance: 'Performance',
          marketing: 'Marketing',
        },
        consentNotice: {
          title: 'Respect de votre vie privée',
          description:
            "Nous utilisons des cookies et traceurs afin d’analyser l'utilisation de la plateforme et vous proposer la meilleure expérience possible. Vous pouvez accepter ou refuser l’activation de leur suivi. À tout moment, vous pouvez consulter et modifier vos choix à partir de la page « Gérer les cookies » dans la rubrique « Aide et support ».",
          learnMore: 'Choisir les cookies',
        },
        consentModal: {
          title: 'Gestion des cookies',
          description:
            'Un cookie est un fichier texte déposé sur votre appareil lors de votre visite sur la plateforme. Nous utilisons les données collectées par ces cookies et traceurs afin de vous proposer la meilleure expérience possible. Vous pouvez accepter ou refuser l’activation de leur suivi. \n' +
            '\n' +
            'Votre choix est conservé pendant 6 mois. À tout moment, vous pouvez consulter et modifier vos préférences à partir de la page « Gérer les cookies » dans la rubrique \n' +
            '« Aide et support ».',
        },
        acceptTitle: 'Tout accepter',
        accept: 'Tout accepter',
        decline: 'Tout refuser',
        save: 'Enregistrer mes choix',
        firebase: {
          description:
            'Ces cookies permettent d’établir des statistiques de fréquentation et de navigation afin d’améliorer votre parcours. Ils permettent par exemple de mesurer la pertinence d’une nouvelle fonctionnalité.',
        },
        hotjar: {
          description:
            'Ces cookies permettent d’analyser vos interactions avec la plateforme de façon anonyme afin d’identifier des points de friction. Ils permettent par exemple de recueillir vos avis grâce à des sondages.',
        },
        sentry: {
          description:
            'Ces cookies sont nécessaires au fonctionnement de la plateforme et ne peuvent être désactivés. Ils permettent par exemple de remonter les erreurs techniques.',
        },
        beamer: {
          description:
            'Ces cookies permettent de vous accompagner de façon personnalisée sur la plateforme grâce à un centre de notifications. Ils permettent par exemple de vous informer des dernières nouveautés et fonctionnalités.',
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
        purposes: ['performance'],
      },
      {
        name: 'beamer',
        title: 'Beamer',
        purposes: ['marketing'],
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
        title: 'Cookies essentiels',
        apps: ['sentry'],
      },
      {
        name: 'personalization',
        title: 'Cookies de statistiques',
        apps: ['firebase'],
      },
      {
        name: 'performance',
        title: 'Cookies de performance',
        apps: ['hotjar'],
      },
      {
        name: 'marketing',
        title: 'Cookies de personnalisation ',
        apps: ['beamer'],
      },
    ],
  }

  let storageId = localStorage.getItem('DEVICE_ID')
  if (storageId == null) {
    localStorage.setItem('DEVICE_ID', uuidv4())
  }
  return Orejime.init(orejimeConfig)
}
