import { parsePhoneNumberFromString } from 'libphonenumber-js'
import * as yup from 'yup'

import { emailSchema } from '@/commons/utils/isValidEmail'
import { extractPhoneParts } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'

import { CollectiveDataFormValues } from './type'

const isPhoneValid = (phone: string | undefined): boolean => {
  if (!phone || !extractPhoneParts(phone).phoneNumber) {
    return true
  }

  const phoneNumber = parsePhoneNumberFromString(phone, 'FR')
  const isValid = phoneNumber?.isValid()
  return Boolean(isValid)
}

export const validationSchema = yup.object<CollectiveDataFormValues>().shape({
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
  collectiveEmail: yup.string().test(emailSchema),
  collectiveDomains: yup.array(),
  collectiveLegalStatus: yup.string(),
  collectiveInterventionArea: yup.array(),
})
