import * as yup from 'yup'

import { validationSchema as accessibilityValidationSchema } from './Accessibility'
import { validationSchema as addressValidationSchema } from './Address'
import { validationSchema as contactValidationSchema } from './Contact'
import { validationSchema as informationsValidationSchema } from './Informations'

const validationSchema = {
  ...informationsValidationSchema,
  ...addressValidationSchema,
  ...accessibilityValidationSchema,
  ...contactValidationSchema,
}

export default yup.object().shape(validationSchema)
