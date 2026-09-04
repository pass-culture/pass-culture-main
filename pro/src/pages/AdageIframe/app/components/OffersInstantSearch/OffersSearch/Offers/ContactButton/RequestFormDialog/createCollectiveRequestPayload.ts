import type { PostCollectiveRequestBodyModel } from '@/apiClient/adage'
import { isDateValid } from '@/commons/utils/date'

import type { RequestFormValues } from './type'

export const createCollectiveRequestPayload = (
  formValues: RequestFormValues
): PostCollectiveRequestBodyModel => {
  return {
    comment: formValues.description,
    phoneNumber: formValues.teacherPhone ? formValues.teacherPhone : null,
    requestedDate: isDateValid(formValues.offerDate)
      ? formValues.offerDate
      : null,
    totalTeachers: formValues.nbTeachers || null,
    totalStudents: formValues.nbStudents || null,
  }
}
