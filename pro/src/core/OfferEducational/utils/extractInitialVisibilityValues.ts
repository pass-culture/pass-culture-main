import { EducationalInstitution, VisibilityFormValues } from '../types'

export const extractInitialVisibilityValues = (
  institution?: EducationalInstitution | null
): VisibilityFormValues => ({
  institution: institution?.id?.toString() ?? '',
  'search-institution': institution
    ? `${institution.name} - ${institution.city}`
    : '',
  visibility: institution ? 'one' : 'all',
})
