import { CollectiveOfferResponseModel } from '@/apiClient/adage'

export function getBookableOfferInstitutionAndTeacherName(
  offer: CollectiveOfferResponseModel
) {
  return offer.educationalInstitution
    ? `${offer.teacher ? `${getTeacherFullName(offer.teacher)} - ` : ''}${offer.educationalInstitution.institutionType || ''} ${offer.educationalInstitution.name}`
    : null
}

function getTeacherFullName(teacher: CollectiveOfferResponseModel['teacher']) {
  return `${teacher?.firstName || ''} ${teacher?.lastName || ''}`
}
