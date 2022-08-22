import * as yup from 'yup'

import { urlRegex } from 'core/shared'
import { isPhoneValid } from 'core/shared/utils/validation'

export const validationSchema = yup.object().shape({
  collectiveDescription: yup.string(),
  collectiveStudents: yup.array(),
  collectiveWebsite: yup.string().test({
    name: 'matchWebsiteUrl',
    message: 'l’URL renseignée n’est pas valide',
    test: (url?: string) => (url ? url.match(urlRegex) !== null : true),
  }),
  collectivePhone: yup.string().test({
    name: 'is-phone-valid',
    message: 'Votre numéro de téléphone n’est pas valide',
    test: isPhoneValid,
  }),
  collectiveEmail: yup.string().email('Votre email n’est pas valide'),
})
