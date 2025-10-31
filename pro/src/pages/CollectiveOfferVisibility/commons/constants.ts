import type { VisibilityFormValues } from './validationSchema'

export const GET_REDACTOR_NOT_FOUND_ERROR_MESSAGE =
  "Nous n'avons pas trouvé d'enseignant correspondant à votre recherche"

export const POST_VISIBILITY_FORM_ERROR_MESSAGE =
  'Une ou plusieurs erreurs sont présentes dans le formulaire'

export const INSTITUTION_GENERIC_ERROR_MESSAGE =
  "Nous n'avons pas trouvé d'établissement correspondant à votre recherche. Veuillez en sélectionner un autre dans la liste."

export const REDACTOR_GENERIC_ERROR_MESSAGE =
  "Nous n'avons pas trouvé d'enseignant correspondant à votre recherche. Veuillez en sélectionner un autre dans la liste."

type BackendFormKeys =
  | 'educationalInstitutionId'
  | 'educationalInstitution'
  | 'teacherEmail'

export const FORM_KEYS_MAPPING: Record<
  BackendFormKeys,
  keyof VisibilityFormValues
> = {
  educationalInstitutionId: 'institution',
  educationalInstitution: 'institution',
  teacherEmail: 'teacher',
}
export const DEFAULT_FORM_FIELD_ERRORS: Record<
  keyof VisibilityFormValues,
  string
> = {
  institution: INSTITUTION_GENERIC_ERROR_MESSAGE,
  teacher: REDACTOR_GENERIC_ERROR_MESSAGE,
  visibility: POST_VISIBILITY_FORM_ERROR_MESSAGE,
}
