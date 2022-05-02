import * as yup from 'yup'

import { validationSchema as informationsSchema } from './Informations'
import { validationSchema as usefulInformationsSchema } from './UsefulInformations'
import { validationSchema as categoriesSchema } from './Categories'

export const validationSchema = yup.object().shape({
  ...informationsSchema,
  ...usefulInformationsSchema,
  ...categoriesSchema,
})
