import { PostCollectiveRequestBodyModel } from 'apiClient/adage'
import { isDateValid } from 'commons/utils/date'

import { RequestFormValues } from './type'

export const createCollectiveRequestPayload = (
  formValues: RequestFormValues
): PostCollectiveRequestBodyModel => {
  return {
    comment: formValues.description,
    phoneNumber: formValues.teacherPhone,
    requestedDate: isDateValid(formValues.offerDate)
      ? new Date(formValues.offerDate).toISOString()
      : undefined,
    totalTeachers: formValues.nbTeachers,
    totalStudents: formValues.nbStudents,
  }
}
