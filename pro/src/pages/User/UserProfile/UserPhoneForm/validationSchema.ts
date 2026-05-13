import * as yup from 'yup'

import { phoneNumberSchema } from '@/commons/utils/yup/phoneNumberSchema'

export const validationSchema = yup.object().shape({
  phoneNumber: phoneNumberSchema().required(
    'Veuillez renseigner un numéro de téléphone'
  ),
})
