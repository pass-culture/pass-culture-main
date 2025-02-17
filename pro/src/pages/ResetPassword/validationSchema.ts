import * as yup from 'yup'

import { passwordValidationStatus } from 'ui-kit/formV2/PasswordInput/validation'

export const validationSchema = yup.object().shape({
  newPasswordValue: yup
    .string()
    .required('Veuillez renseigner un mot de passe')
    .test(
      'isPasswordValid',
      'Veuillez renseigner un mot de passe valide avec : ',
      (passwordValue) => {
        const errors = passwordValidationStatus(passwordValue)
        const hasError = Object.values(errors).some((error) => error)
        return !hasError
      }
    ),
})
