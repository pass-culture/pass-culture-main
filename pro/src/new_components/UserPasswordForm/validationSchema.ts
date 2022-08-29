import * as yup from 'yup'

import { isPasswordValid } from 'core/shared/utils/validation'

const passwordErrorMessage = `Votre mot de passe doit contenir au moins :
      - 12 caractères
      - Un chiffre
      - Une majuscule et une minuscule
      - Un caractère spécial
`

const validationSchema = yup.object().shape({
  oldPassword: yup
    .string()
    .required('Veuillez renseigner votre ancien mot de passe'),
  newPassword: yup
    .string()
    .test('isPasswordValid', passwordErrorMessage, isPasswordValid)
    .required('Veuillez renseigner votre nouveau mot de passe'),
  newConfirmationPassword: yup
    .string()
    .oneOf(
      [yup.ref('newPassword'), ''],
      'Vos nouveaux mots de passe ne correspondent pas'
    )
    .required('Veuillez confirmer votre nouveau mot de passe'),
})

export default validationSchema
