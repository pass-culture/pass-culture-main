import * as yup from 'yup'

import { validationSchema as accessibilityValidationSchema } from './Accessibility'
import { validationSchema as activitySchema } from './Activity'
import { validationSchema as contactValidationSchema } from './Contact'
import { validationSchema as informationsValidationSchema } from './Informations'

const validationSchemaConcat = (newOnboardingActive: boolean) => {
  return {
    ...informationsValidationSchema(newOnboardingActive),
    ...activitySchema(newOnboardingActive),
    ...accessibilityValidationSchema,
    ...contactValidationSchema,
    addressAutocomplete: yup.string().when('isVenueVirtual', {
      is: false,
      then: yup
        .string()
        .required('Veuillez sélectionner une adresse parmi les suggestions'),
    }),
  }
}

const validationSchema = (newOnboardingActive: boolean) =>
  yup.object().shape(validationSchemaConcat(newOnboardingActive))

export default validationSchema
