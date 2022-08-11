import * as yup from 'yup'

import { validationSchema as informationsValidationSchema } from './Informations'

const validationSchema = {
  ...informationsValidationSchema,
}

export default yup.object().shape(validationSchema)
