import { PostCollectiveRequestBodyModel } from 'apiClient/adage'
import { isDateValid } from 'commons/utils/date'

import { RequestFormValues } from './type'

export const createCollectiveRequestPayload = (
  formValues: RequestFormValues
): PostCollectiveRequestBodyModel => {
  return {
    comment: formValues.description,
    phoneNumber: formValues.teacherPhone ? formValues.teacherPhone : undefined,
    requestedDate: isDateValid(formValues.offerDate)
      ? formValues.offerDate
      : undefined,
    totalTeachers: formValues.nbTeachers,
    totalStudents: formValues.nbStudents,
  }
}
