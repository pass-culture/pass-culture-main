import {
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
} from 'apiClient/v1'

import { VisibilityFormValues } from '../types'

export const extractInitialVisibilityValues = (
  institution?: EducationalInstitutionResponseModel | null,
  teacher?: EducationalRedactorResponseModel | null
): VisibilityFormValues => ({
  institution: institution?.id?.toString() ?? '',
  'search-institution': institution
    ? `${institution.name} - ${institution.city}`
    : '',
  teacher: teacher ? `${teacher.email}` : null,
  visibility: institution ? 'one' : 'all',
  'search-teacher': teacher ? `${teacher.firstName} ${teacher.lastName}` : '',
})
