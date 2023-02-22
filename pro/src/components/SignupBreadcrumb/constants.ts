export const SIGNUP_STEP_IDS = {
  AUTHENTICATION: 'authentification',
  ACTIVITY: 'activité',
  VALIDATION: 'validation',
}

export const STEP_LIST = [
  {
    id: SIGNUP_STEP_IDS.AUTHENTICATION,
    label: 'Authentification',
    url: '/signup/authentification',
  },
  {
    id: SIGNUP_STEP_IDS.ACTIVITY,
    label: 'Activité',
    url: '/signup/activite',
  },
  {
    id: SIGNUP_STEP_IDS.VALIDATION,
    label: 'Validation',
    url: '/signup/validation',
  },
]
