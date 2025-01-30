import * as yup from 'yup'

import { isPhoneValid } from 'commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'

export const validationSchema = yup.object().shape({
  phoneNumber: yup
    .string()
    .min(10, 'Veuillez renseigner au moins 10 chiffres')
    .max(20, 'Veuillez renseigner moins de 20 chiffres')
    .required('Veuillez renseigner votre numéro de téléphone')
    .test({
      name: 'is-phone-valid',
      message: 'Votre numéro de téléphone n’est pas valide',
      test: (phone?: string | null) => {
        return phone ? isPhoneValid(phone) : true
      },
    })
})
