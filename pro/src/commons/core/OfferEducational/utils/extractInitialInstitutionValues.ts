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
): InstitutionFormValues => {
  const teacherEmailFromRequest = requestInformations
    ? `${requestInformations.redactor.email}`
    : ''
  const teacherNameFromRequest = requestInformations
    ? `${requestInformations.redactor.firstName} ${requestInformations.redactor.lastName}`
    : ''

  return {
    institution: institution?.id.toString() ?? '',
    teacherEmail: teacher ? `${teacher.email}` : teacherEmailFromRequest,
    teacherName: teacher
      ? `${teacher.firstName} ${teacher.lastName}`
      : teacherNameFromRequest,
  }
}
