import * as yup from 'yup'

import { validationSchema as informationsSchema } from './Informations'

export const validationSchema = yup.object().shape({
  ...informationsSchema,
})
