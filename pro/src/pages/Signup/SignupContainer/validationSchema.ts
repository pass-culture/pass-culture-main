import * as yup from 'yup'

import { emailSchema } from 'commons/utils/isValidEmail'
import { passwordValidationStatus } from 'ui-kit/formV2/PasswordInput/validation'
import { phoneValidationSchema } from 'ui-kit/form/PhoneNumberInput/phoneValidationSchema'

export const validationSchema = (newSignup: boolean) => {
  const schema = yup.object().shape({
    email: yup
      .string()
      .test(emailSchema)
      .required('Veuillez renseigner une adresse email'),
    password: yup
      .string()
      .required('Veuillez renseigner un mot de passe')
      .test(
        'isPasswordValid',
        'Veuillez renseigner un mot de passe valide avec : ',
        (paswordValue) => {
          const errors = passwordValidationStatus(paswordValue)
          const hasError = Object.values(errors).some((error) => error)
          return !hasError
        }
      ),
    lastName: yup.string().max(128).required('Veuillez renseigner votre nom'),
    firstName: yup
      .string()
      .max(128)
      .required('Veuillez renseigner votre prénom'),
    contactOk: yup.string(),
  })
  if (newSignup) {
    return schema
  } else {
    return schema.concat(phoneValidationSchema)
  }
}
