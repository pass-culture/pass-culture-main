import { format } from 'date-fns'

import { PostCollectiveRequestBodyModel } from 'apiClient/adage'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'

import { RequestFormValues } from '../type'

export const createCollectiveRequestPayload = (
  formValues: RequestFormValues
): PostCollectiveRequestBodyModel => {
  return {
    comment: formValues.description,
    phoneNumber: formValues.teacherPhone,
    requestedDate: formValues.offerDate
      ? format(formValues.offerDate, FORMAT_ISO_DATE_ONLY)
      : undefined,
    totalTeachers: formValues.nbTeachers,
    totalStudents: formValues.nbStudents,
  }
}
