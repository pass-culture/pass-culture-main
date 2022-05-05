import * as yup from 'yup'

import { validationSchema as informationsSchema } from './Informations'
import { validationSchema as venueSchema } from './Venue'

export const validationSchema = yup.object().shape({
  ...informationsSchema,
  ...venueSchema,
})
