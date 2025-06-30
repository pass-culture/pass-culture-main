import * as yup from 'yup'

import { isPasswordValid } from 'ui-kit/form/PasswordInput/validation'

export const validationSchema = (is2025SignUpEnabled: boolean) => {
  // If the FF WIP_2025_SIGN_UP is enabled, we have a confirmation field
  if (is2025SignUpEnabled) {
    return yup.object().shape({
      newPassword: yup
        .string()
        .required()
        .test('isPasswordValid', isPasswordValid),

      // Adds "newConfirmationPassword" validation
      newConfirmationPassword: yup
        .string()
        .oneOf(
          [yup.ref('newPassword')],
          'Vos nouveaux mots de passe ne correspondent pas'
        )
        .required('Veuillez confirmer votre nouveau mot de passe'),
    })
  } else {
    return yup.object().shape({
      newPassword: yup
        .string()
        .required()
        .test('isPasswordValid', isPasswordValid),
    })
  }
}
