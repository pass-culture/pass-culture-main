import * as yup from 'yup'

import { emailSchema } from '@/commons/utils/isValidEmail'
import { phoneNumberSchema } from '@/commons/utils/yup/phoneNumberSchema'

import type { RequestFormValues } from './type'

export const validationSchema = yup.object<RequestFormValues>().shape({
  teacherEmail: yup
    .string()
    .max(120)
    .test(emailSchema)
    .required('Veuillez renseigner une adresse email'),
  teacherPhone: phoneNumberSchema(),
  offerDate: yup.string(),
  offerTime: yup.string(),
  nbStudents: yup
    .number()
    .transform((value) => (Number.isNaN(value) ? undefined : value))
    .min(0, 'Nombre positif attendu'),
  nbTeachers: yup
    .number()
    .transform((value) => (Number.isNaN(value) ? undefined : value))
    .min(0, 'Nombre positif attendu'),
  description: yup
    .string()
    .nullable()
    .max(1000)
    .required('Veuillez préciser votre demande'),
})
