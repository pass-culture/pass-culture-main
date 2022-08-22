import * as yup from 'yup'

import { validationSchema as contactValidationSchema } from './Contact'
import { validationSchema as informationsValidationSchema } from './Informations'

const validationSchema = {
  ...informationsValidationSchema,
  ...contactValidationSchema,
}

export default yup.object().shape(validationSchema)
