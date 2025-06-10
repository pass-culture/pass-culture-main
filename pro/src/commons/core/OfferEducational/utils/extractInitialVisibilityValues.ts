import {
  CollectiveOfferInstitutionModel,
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
  GetCollectiveOfferRequestResponseModel,
} from 'apiClient/v1'
import { VisibilityFormValues } from 'pages/CollectiveOfferVisibility/components/CollectiveOfferVisibility/CollectiveOfferVisibility'

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
  institution: institution?.id.toString() ?? '',
  teacher: teacher
    ? `${teacher.email}`
    : requestInformations
      ? `${requestInformations.redactor.email}`
      : undefined,
  visibility: institution || requestInformations ? 'one' : 'all',
})
