import { EducationalInstitutionResponseModel } from 'apiClient/v1'

import { VisibilityFormValues } from '../types'

export const extractInitialVisibilityValues = (
  institution?: EducationalInstitutionResponseModel | null
): VisibilityFormValues => ({
  institution: institution?.id?.toString() ?? '',
  'search-institution': institution
    ? `${institution.name} - ${institution.city}`
    : '',
  visibility: institution ? 'one' : 'all',
})
