import type {
  CollectiveOfferInstitutionModel,
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
  GetCollectiveOfferRequestResponseModel,
} from '@/apiClient/v1'
import type { InstitutionFormValues } from '@/pages/CollectiveOfferInstitution/commons/validationSchema'

export const formatInstitutionDisplayName = (
  institution:
    | EducationalInstitutionResponseModel
    | CollectiveOfferInstitutionModel
) => {
  return `${institution.institutionType || ''} ${institution.name} - ${
    institution.city
  } - ${institution.institutionId}`.trim()
}

export const extractInitialInstitutionValues = (
  institution?: EducationalInstitutionResponseModel | null,
  teacher?: EducationalRedactorResponseModel | null,
  requestInformations?: GetCollectiveOfferRequestResponseModel | null
): InstitutionFormValues => ({
  institution: institution?.id.toString() ?? '',
  teacherEmail: teacher
    ? `${teacher.email}`
    : requestInformations
      ? `${requestInformations.redactor.email}`
      : '',
  teacherName: teacher ? `${teacher.firstName} ${teacher.lastName}` : '',
})
