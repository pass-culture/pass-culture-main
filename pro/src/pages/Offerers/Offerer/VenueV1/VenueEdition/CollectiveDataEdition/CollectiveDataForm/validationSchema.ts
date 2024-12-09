import * as yup from 'yup'

import { isPhoneValid } from 'commons/core/shared/utils/validation'

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
    test: (phone) => isPhoneValid({ phone, emptyAllowed: true }),
  }),
  collectiveEmail: yup
    .string()
    .email('Veuillez renseigner un email valide, exemple : mail@exemple.com'),
})
