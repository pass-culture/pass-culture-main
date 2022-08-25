import * as yup from 'yup'

import { urlRegex } from 'core/shared'
import { isPhoneValid } from 'core/shared/utils/validation'

const validationSchema = {
  phoneNumber: yup
    .string()
    .required('Veuillez renseigner un numéro de téléphone')
    .test({
      name: 'is-phone-valid',
      message: 'Le numéro de téléphone n’est pas valide',
      test: isPhoneValid,
    }),
  email: yup
    .string()
    .required('Votre email n’est pas valide')
    .email(
      'L’e-mail renseigné n’est pas valide. Exemple : votrenom@votremail.com'
    ),
  webSiteAddress: yup.string().test({
    name: 'matchWebsiteUrl',
    message: 'l’URL renseignée n’est pas valide',
    test: (url?: string) => (url ? url.match(urlRegex) !== null : true),
  }),
}

export default validationSchema
