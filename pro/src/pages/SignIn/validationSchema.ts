import * as yup from 'yup'

import { emailSchema } from '@/commons/utils/isValidEmail'

export const validationSchema = yup.object().shape({
  email: yup
    .string()
    .test(emailSchema)
    .required('Veuillez renseigner une adresse email'),
  password: yup.string().required('Veuillez renseigner un mot de passe'),
})
