import * as yup from 'yup'

import { phoneNumberSchema } from '@/ui-kit/form/PhoneNumberInput/commons/phoneNumberSchema'

export const validationSchema = yup.object().shape({
  phoneNumber: phoneNumberSchema().required(
    'Veuillez renseigner un numéro de téléphone'
  ),
})
