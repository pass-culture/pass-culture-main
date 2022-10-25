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
    .required('Veuillez renseigner une adresse e-mail')
    .email('Veuillez renseigner un e-mail valide'),
  webSiteAddress: yup.string().test({
    name: 'matchWebsiteUrl',
    message: 'Veuillez renseigner une URL valide. Ex : https://exemple.com',
    test: (url?: string) => {
      /* istanbul ignore next: DEBT, TO FIX */
      return url ? url.match(urlRegex) !== null : true
    },
  }),
  bookingEmail: yup
    .string()
    .required('Veuillez renseigner une adresse e-mail')
    .email('Veuillez renseigner un e-mail valide'),
}

export default validationSchema
