import * as yup from 'yup'

import { isPasswordValid } from 'core/shared/utils/validation'

const passwordErrorMessage = `Votre mot de passe doit contenir au moins :
      - 12 caractères
      - Un chiffre
      - Une majuscule et une minuscule
      - Un caractère spécial
`

export const validationSchema = yup.object().shape({
  newPasswordValue: yup
    .string()
    .required('Veuillez renseigner un mot de passe')
    .test('isPasswordValid', passwordErrorMessage, isPasswordValid),
})
