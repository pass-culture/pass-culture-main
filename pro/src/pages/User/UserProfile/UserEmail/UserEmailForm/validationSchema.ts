import { emailSchema } from 'commons/utils/isValidEmail'
import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  email: yup
    .string()
    .max(120)
    .test(emailSchema)
    .required('Veuillez renseigner votre nouvel email'),
  password: yup
    .string()
    .max(128)
    .required('Veuillez renseigner votre mot de passe'),
})
