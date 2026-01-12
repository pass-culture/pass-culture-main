import * as yup from 'yup'

import { emailSchema } from '@/commons/utils/isValidEmail'

export const validationSchema = yup.object().shape({
  email: yup
    .string()
    .required('Veuillez renseigner une adresse email')
    .test(emailSchema),
  password: yup.string().required('Veuillez renseigner un mot de passe'),
  lastName: yup.string().max(128).required('Veuillez renseigner votre nom'),
  firstName: yup.string().max(128).required('Veuillez renseigner votre prénom'),
  contactOk: yup.boolean().default(false), // optional field, but defaults to "false"
  token: yup.string().default(''), // this allows to pass hookForm validation and set the token after form submission
})
