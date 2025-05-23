import * as yup from 'yup'

import { isPhoneValid } from 'commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'

export const validationSchema = yup.object().shape({
  phoneNumber: yup
    .string()
    .required('Veuillez renseigner votre numéro de téléphone')
    .test(
      'isPhoneValid',
      'Votre numéro de téléphone n’est pas valide',
      isPhoneValid
    ),
})
