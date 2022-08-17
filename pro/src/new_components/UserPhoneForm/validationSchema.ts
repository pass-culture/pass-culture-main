import * as yup from 'yup'

import { parseAndValidateFrenchPhoneNumber } from 'core/shared/utils/parseAndValidateFrenchPhoneNumber'

const validationSchema = yup.object().shape({
  phoneNumber: yup
    .string()
    .min(10, 'Veuillez renseigner au moins 10 chiffres')
    .max(20, 'Veuillez renseigner moins de 20 chiffres')
    .required('Veuillez renseigner votre numéro de téléphone')
    .test(
      'isPhoneValid',
      'Votre numéro de téléphone n’est pas valide',
      value => {
        if (!value) return false
        const phoneNumber = parseAndValidateFrenchPhoneNumber(value)
        const isValid = phoneNumber?.isValid()
        if (!isValid) return false
        return true
      }
    ),
})

export default validationSchema
