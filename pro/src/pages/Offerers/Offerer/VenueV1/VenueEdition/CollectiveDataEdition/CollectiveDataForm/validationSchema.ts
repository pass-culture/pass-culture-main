import { parsePhoneNumberFromString } from 'libphonenumber-js'
import * as yup from 'yup'

import { urlRegex } from 'core/shared'

const isPhoneValid = (phone: string | undefined): boolean => {
  if (!phone) {
    return true
  }

  const phoneNumber = parsePhoneNumberFromString(phone, 'FR')
  const isValid = phoneNumber?.isValid()
  return Boolean(isValid)
}

export const validationSchema = yup.object().shape({
  collectiveDescription: yup.string(),
  collectiveStudents: yup.array(),
  collectiveWebsite: yup.string().test({
    name: 'matchWebsiteUrl',
    message: 'Veuillez renseigner une URL valide. Ex : https://exemple.com',
    test: (url?: string) => (url ? url.match(urlRegex) !== null : true),
  }),
  collectivePhone: yup.string().test({
    name: 'is-phone-valid',
    message:
      'Veuillez entrer un numéro de téléphone valide, exemple : 612345678',
    test: isPhoneValid,
  }),
  collectiveEmail: yup
    .string()
    .email('Veuillez renseigner un email valide, exemple : mail@exemple.com'),
})
