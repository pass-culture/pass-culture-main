import type { CollectiveOfferResponseModel } from '@/apiClient/adage'

export function getBookableOfferInstitutionAndTeacherName(
  offer: CollectiveOfferResponseModel
) {
  const teacherName = offer.teacher
    ? `${getTeacherFullName(offer.teacher)} - `
    : ''
  return offer.educationalInstitution
    ? `${teacherName}${offer.educationalInstitution.institutionType || ''} ${offer.educationalInstitution.name}`
    : null
}

function getTeacherFullName(teacher: CollectiveOfferResponseModel['teacher']) {
  return `${teacher?.firstName || ''} ${teacher?.lastName || ''}`
}
