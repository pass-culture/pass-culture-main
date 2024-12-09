import * as yup from 'yup'

import { isPhoneValid } from 'commons/core/shared/utils/validation'

export const validationSchema = yup.object().shape({
  phoneNumber: yup
    .string()
    .min(10, 'Veuillez renseigner au moins 10 chiffres')
    .max(20, 'Veuillez renseigner moins de 20 chiffres')
    .required('Veuillez renseigner votre numéro de téléphone')
    .test(
      'isPhoneValid',
      'Votre numéro de téléphone n’est pas valide',
      (phone) => isPhoneValid({ phone, emptyAllowed: false })
    ),
})
