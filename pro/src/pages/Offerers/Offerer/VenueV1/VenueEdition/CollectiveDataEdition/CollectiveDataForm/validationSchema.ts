import { parsePhoneNumberFromString } from 'libphonenumber-js'
import * as yup from 'yup'

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
  collectiveWebsite: yup
    .string()
    .url('Veuillez renseigner une URL valide. Ex : https://exemple.com'),
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
