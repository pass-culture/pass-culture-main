import { api } from 'apiClient/api'
import { toISOStringWithoutMilliseconds } from 'commons/utils/date'
import { storageAvailable } from 'commons/utils/storageAvailable'

export enum Consents {
  FIREBASE = 'firebase',
  HOTJAR = 'hotjar',
  BEAMER = 'beamer',
  SENTRY = 'sentry',
}

export const LOCAL_STORAGE_DEVICE_ID_KEY = 'DEVICE_ID'

const mandatoryCookies = ['sentry']

export const orejimeConfig = {
  privacyPolicyUrl: 'https://pass.culture.fr/politique-de-cookies/',
  cookie: {
    duration: 182,
    stringify: (contents: any) => {
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
        deviceId: storageAvailable('localStorage')
          ? (localStorage.getItem(LOCAL_STORAGE_DEVICE_ID_KEY) ?? 'NODEVICEID')
          : 'NODEVICEID',
      }

      // l’api orejime n’est pas asynchrone
      api.cookiesConsent(cookieConsent)

      return JSON.stringify(contents)
    },
    parse: (cookie: string) => {
      return JSON.parse(cookie)
    },
    sameSite: 'strict',
    name: 'orejime',
  },
  orejimeElement: '#orejimeElement',
  translations: {
    banner: {
      title: 'Respect de votre vie privée',
      description:
        'Nous utilisons des cookies et traceurs afin d’analyser l’utilisation de la plateforme et vous proposer la meilleure expérience possible. Vous pouvez accepter ou refuser l’activation de leur suivi. À tout moment, vous pouvez consulter et modifier vos choix à partir de la page « Gérer les cookies » dans la rubrique « Aide et support ».',
      accept: 'Tout accepter',
      acceptTitle: 'Tout accepter',
      decline: 'Tout refuser',
      declineTitle: 'Tout refuser',
      configure: 'Gestion des cookies',
      configureTitle: 'Gestion des cookies',
    },
    modal: {
      title: 'Gestion des cookies',
      description:
        'Un cookie est un fichier texte déposé sur votre appareil lors de votre visite sur la plateforme. Nous utilisons les données collectées par ces cookies et traceurs afin de vous proposer la meilleure expérience possible. Vous pouvez accepter ou refuser l’activation de leur suivi. Votre choix est conservé pendant 6 mois. Les cookies mentionnés ci-dessous sont ceux pour lesquels votre consentement est requis. À tout moment, vous pouvez consulter et modifier vos préférences à partir de la page « Gérer les cookies » dans la rubrique « Aide et support ». Pour en savoir plus, notamment sur les cookies dits "essentiels", merci de consulter notre {privacyPolicy}.',
      save: 'Enregistrer mes choix',
    },
    acceptTitle: 'Tout accepter',
    accept: 'Tout accepter',
    decline: 'Tout refuser',
    save: 'Enregistrer mes choix',
  },
  purposes: [
    {
      id: 'stats',
      title: 'Statistiques',
      purposes: [
        {
          id: Consents.FIREBASE,
          title: 'Firebase  (Google Analytics)',
          cookies: [/_ga.*/],
          description:
            'Ces cookies permettent d’établir des statistiques de fréquentation et de navigation afin d’améliorer votre parcours. Ils permettent par exemple de mesurer la pertinence d’une nouvelle fonctionnalité.',
        },
      ],
    },
    {
      id: 'perfs',
      title: 'Performance',
      purposes: [
        {
          id: Consents.HOTJAR,
          title: 'Hotjar',
          cookies: /_hs.*/,
          description:
            'Ces cookies permettent d’analyser vos interactions avec la plateforme de façon anonyme afin d’identifier des points de friction. Ils permettent par exemple de recueillir vos avis grâce à des sondages.',
        },
      ],
    },
    {
      id: 'perso',
      title: 'Personnalisation',
      purposes: [
        {
          id: Consents.BEAMER,
          title: 'Beamer',
          description:
            'Ces cookies permettent de vous accompagner de façon personnalisée sur la plateforme grâce à un centre de notifications. Ils permettent par exemple de vous informer des dernières nouveautés et fonctionnalités.',
          cookies: /_BEAMER.*/,
        },
      ],
    },
    {
      id: 'required',
      title: 'Essentiels',
      purposes: [
        {
          id: Consents.SENTRY,
          title: 'Sentry',
          description:
            'Ces cookies sont nécessaires au fonctionnement de la plateforme et ne peuvent être désactivés. Ils permettent par exemple de remonter les erreurs techniques.',
          cookies: ['sentrysid'],
          isMandatory: true,
          default: true,
        },
      ],
    },
  ],
}
