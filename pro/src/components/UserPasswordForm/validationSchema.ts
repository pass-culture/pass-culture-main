import * as yup from 'yup'

import { isPasswordValid } from 'ui-kit/formV2/PasswordInput/validation'

export const validationSchema = yup.object().shape({
  oldPassword: yup
    .string()
    .required('Veuillez renseigner votre mot de passe actuel'),
  newPassword: yup
    .string()
    .required('Veuillez renseigner votre nouveau mot de passe')
    .test(
      'isPasswordValid',
      'Veuillez respecter le format requis :',
      isPasswordValid
    ),
  newConfirmationPassword: yup
    .string()
    .oneOf(
      [yup.ref('newPassword'), ''],
      'Vos nouveaux mots de passe ne correspondent pas'
    )
    .required('Veuillez confirmer votre nouveau mot de passe'),
})
