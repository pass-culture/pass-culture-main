import * as yup from 'yup'

import { validationSchema as accessibilityValidationSchema } from './Accessibility'
import { validationSchema as activitySchema } from './Activity'
import { validationSchema as contactValidationSchema } from './Contact'
import { validationSchema as informationsValidationSchema } from './Informations'

const validationSchemaConcat = {
  ...informationsValidationSchema,
  ...activitySchema,
  ...accessibilityValidationSchema,
  ...contactValidationSchema,
  isVenueVirtual: yup.boolean(),
  addressAutocomplete: yup.string().when('isVenueVirtual', {
    is: false,
    then: schema =>
      schema.required(
        'Veuillez sélectionner une adresse parmi les suggestions'
      ),
  }),
}

const validationSchema = yup.object().shape(validationSchemaConcat)

export default validationSchema
