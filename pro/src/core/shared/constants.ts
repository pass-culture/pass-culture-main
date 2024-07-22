import { StudentLevels } from 'apiClient/v1'

export const PATCH_SUCCESS_MESSAGE =
  'Vos modifications ont bien été enregistrées'
export const GET_DATA_ERROR_MESSAGE =
  'Nous avons rencontré un problème lors de la récupération des données.'
export const RECAPTCHA_ERROR = 'Error while loading recaptcha'
export const RECAPTCHA_ERROR_MESSAGE = 'Une erreur technique est survenue'
export const SENT_DATA_ERROR_MESSAGE =
  'Une erreur est survenue lors de la sauvegarde de vos modifications.\n Merci de réessayer plus tard'
export const FORM_ERROR_MESSAGE =
  'Une ou plusieurs erreurs sont présentes dans le formulaire'

export const NBSP = '\u00a0'

export const SAVED_OFFERER_ID_KEY = 'homepageSelectedOffererId'

export const DEFAULT_MARSEILLE_STUDENTS = [
  StudentLevels._COLES_MARSEILLE_MATERNELLE,
  StudentLevels._COLES_MARSEILLE_CP_CE1_CE2,
  StudentLevels._COLES_MARSEILLE_CM1_CM2,
]
