import * as yup from 'yup'

import { validationSchema as accessibilityValidationSchema } from './Accessibility'
import { validationSchema as activitySchema } from './Activity'
import { validationSchema as addressValidationSchema } from './Address'
import { validationSchema as contactValidationSchema } from './Contact'
import { validationSchema as informationsValidationSchema } from './Informations'

const validationSchemaConcat = (newOnboardingActive: boolean) => {
  return {
    ...informationsValidationSchema(newOnboardingActive),
    ...addressValidationSchema,
    ...activitySchema(newOnboardingActive),
    ...accessibilityValidationSchema,
    ...contactValidationSchema,
  }
}

const validationSchema = (newOnboardingActive: boolean) =>
  yup.object().shape(validationSchemaConcat(newOnboardingActive))

export default validationSchema
