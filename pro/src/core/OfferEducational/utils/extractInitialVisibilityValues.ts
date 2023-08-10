import {
  CollectiveOfferInstitutionModel,
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
  GetCollectiveOfferRequestResponseModel,
} from 'apiClient/v1'

import { VisibilityFormValues } from '../types'

export const formatInstitutionDisplayName = (
  institution:
    | EducationalInstitutionResponseModel
    | CollectiveOfferInstitutionModel
) => {
  return `${institution.institutionType || ''} ${institution.name} - ${
    institution.city
  } - ${institution.institutionId}`.trim()
}

export const extractInitialVisibilityValues = (
  institution?: EducationalInstitutionResponseModel | null,
  teacher?: EducationalRedactorResponseModel | null,
  requestInformations?: GetCollectiveOfferRequestResponseModel | null
): VisibilityFormValues => ({
  institution: institution?.id?.toString() ?? '',
  'search-institution': institution
    ? formatInstitutionDisplayName(institution)
    : requestInformations
    ? formatInstitutionDisplayName(requestInformations.institution)
    : '',
  teacher: teacher
    ? `${teacher.email}`
    : requestInformations
    ? `${requestInformations.redactor.email}`
    : null,
  visibility: institution || requestInformations ? 'one' : 'all',
  'search-teacher': teacher
    ? `${teacher.firstName} ${teacher.lastName}`
    : requestInformations
    ? `${requestInformations.redactor.firstName} ${requestInformations.redactor.lastName}`
    : '',
})
