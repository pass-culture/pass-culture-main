import { Step } from 'components/Breadcrumb'

export enum SIGNUP_JOURNEY_STEP_IDS {
  WELCOME = 'inscription',
  OFFERER = 'structure',
  OFFERERS = 'strutures',
  AUTHENTICATION = 'authentification',
  ACTIVITY = 'activite',
  VALIDATION = 'validation',
}

export const SIGNUP_JOURNEY_BREADCRUMB_STEPS: Step[] = [
  {
    id: SIGNUP_JOURNEY_STEP_IDS.AUTHENTICATION,
    label: 'Authentification',
    url: '/parcours-inscription/authentification',
  },
  {
    id: SIGNUP_JOURNEY_STEP_IDS.ACTIVITY,
    label: 'Activité',
    url: '/parcours-inscription/activite',
  },
  {
    id: SIGNUP_JOURNEY_STEP_IDS.VALIDATION,
    label: 'Validation',
    url: '/parcours-inscription/validation',
  },
]
