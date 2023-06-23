import * as yup from 'yup'

import { passwordValidationStatus } from 'core/shared/utils/validation'

export const validationSchema = yup.object().shape({
  newPasswordValue: yup
    .string()
    .required('Veuillez renseigner un mot de passe')
    .test(
      'isPasswordValid',
      'Veuillez renseigner un mot de passe valide avec : ',
      paswordValue => {
        const errors = passwordValidationStatus(paswordValue)
        const hasError = Object.values(errors).some(e => e === true)
        return !hasError
      }
    ),
})
