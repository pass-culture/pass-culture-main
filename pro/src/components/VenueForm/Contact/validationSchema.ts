import * as yup from 'yup'

import { urlRegex } from 'core/shared'
import { isPhoneValid } from 'core/shared/utils/validation'

const validationSchema = {
  phoneNumber: yup
    .string()
    .nullable()
    .test({
      name: 'is-phone-valid',
      message: 'Veuillez entrer un numéro de téléphone valide',
      test: (phone?: string | null) => {
        /* istanbul ignore next: DEBT, TO FIX */
        return phone ? isPhoneValid(phone) : true
      },
    }),
  email: yup.string().nullable().email('Veuillez renseigner un email valide'),
  webSite: yup
    .string()
    .nullable()
    .test({
      name: 'matchWebsiteUrl',
      message: 'Veuillez renseigner une URL valide. Ex : https://exemple.com',
      test: (url?: string | null) => {
        /* istanbul ignore next: DEBT, TO FIX */
        return url ? url.match(urlRegex) !== null : true
      },
    }),
  isVenueVirtual: yup.boolean(),
  bookingEmail: yup
    .string()
    .email('Veuillez renseigner un email valide')
    .when('isVenueVirtual', {
      is: false,
      then: schema => schema.required('Veuillez renseigner une adresse email'),
    }),
}

export default validationSchema
