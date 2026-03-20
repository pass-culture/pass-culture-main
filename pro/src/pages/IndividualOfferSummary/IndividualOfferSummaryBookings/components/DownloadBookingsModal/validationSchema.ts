import * as yup from 'yup'

import { BookingsExportStatusFilter } from '@/apiClient/v1'

export const validationSchema = yup.object().shape({
  selectedDate: yup.string().required('Vous devez sélectionner  une date'),
  selectedBookingType: yup
    .string()
    .oneOf(Object.values(BookingsExportStatusFilter))
    .required(),
})
