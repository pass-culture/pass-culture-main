import * as yup from 'yup'

import { emailSchema } from '@/commons/utils/isValidEmail'

export const validationSchema = yup.object().shape({
  email: yup
    .string()
    .max(120)
    .test(emailSchema)
    .required('Veuillez renseigner votre nouvel email'),
})
