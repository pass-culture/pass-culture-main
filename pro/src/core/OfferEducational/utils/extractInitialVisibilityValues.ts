import { EducationalInstitution, VisibilityFormValues } from '../types'

export const extractInitialVisibilityValues = (
  institution?: EducationalInstitution | null
): VisibilityFormValues => ({
  institution: institution?.id?.toString() ?? '',
  'search-institution': institution?.name ?? '',
  visibility: institution ? 'one' : 'all',
})
