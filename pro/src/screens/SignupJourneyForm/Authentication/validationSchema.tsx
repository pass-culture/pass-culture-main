import * as yup from 'yup'

import { validationSchema as addressValidationSchema } from 'components/Address/validationSchema'

export const validationSchema = yup.object().shape({
  siret: yup.string().required(),
  name: yup.string().required(),
  publicName: yup.string().nullable(),
  ...addressValidationSchema,
})
