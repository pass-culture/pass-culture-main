import * as yup from 'yup'

import { emailSchema } from '@/commons/utils/isValidEmail'

export const getValidationSchema = (userEmail: string) => {
  return yup.object().shape({
    email: yup
      .string()
      .required(
        'Veuillez renseigner votre email pour confirmer la suppression du compte'
      )
      .test(emailSchema)
      .test({
        name: 'matchesUserEmail',
        message: "L'adresse email ne correspond pas à celle de votre compte",
        test: (value) => value === userEmail,
      }),
  })
}
