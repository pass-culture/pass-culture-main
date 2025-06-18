import { parsePhoneNumberFromString } from 'libphonenumber-js'
import * as yup from 'yup'

import { emailSchema } from 'commons/utils/isValidEmail'

const isPhoneValid = (phone: string | undefined): boolean => {
  if (!phone) {
    return true
  }

  const phoneNumber = parsePhoneNumberFromString(phone, 'FR')
  const isValid = phoneNumber?.isValid()
  return Boolean(isValid)
}

export const validationSchema =
  yup.object().shape({
    teacherEmail: yup
      .string()
      .max(120)
      .test(emailSchema)
      .required('Veuillez renseigner une adresse email'),
    teacherPhone: yup.string().test({
      name: 'is-phone-valid',
      message: 'Veuillez renseigner un numéro de téléphone valide',
      test: isPhoneValid,
    }),
    offerDate: yup.string(),
    nbStudents: yup.number().transform((value) => (Number.isNaN(value) ? undefined : value)).min(0, 'Nombre positif attendu'),
    nbTeachers: yup.number().transform((value) => (Number.isNaN(value) ? undefined : value)).min(0, 'Nombre positif attendu'),
    description: yup
      .string()
      .nullable()
      .max(1000)
      .required('Veuillez préciser votre demande'),
  })
