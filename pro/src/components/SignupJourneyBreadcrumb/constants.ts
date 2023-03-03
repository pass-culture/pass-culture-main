export enum SIGNUP_STEP_IDS {
  OFFERER = 'structure',
  AUTHENTICATION = 'authentification',
  ACTIVITY = 'activite',
  VALIDATION = 'validation',
}

export const SIGNUP_JOURNEY_STEP_LIST = [
  {
    id: SIGNUP_STEP_IDS.AUTHENTICATION,
    label: 'Authentification',
    url: '/parcours-inscription/authentification',
  },
  {
    id: SIGNUP_STEP_IDS.ACTIVITY,
    label: 'Activité',
    url: '/parcours-inscription/activite',
  },
  {
    id: SIGNUP_STEP_IDS.VALIDATION,
    label: 'Validation',
    url: '/parcours-inscription/validation',
  },
]
