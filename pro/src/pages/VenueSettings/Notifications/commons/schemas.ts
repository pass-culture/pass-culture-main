import * as yup from 'yup'

import { emailSchema } from '@/commons/utils/isValidEmail'
import { nonEmptyStringOrNull } from '@/commons/utils/yup/nonEmptyStringOrNull'

export const VenueSettingsNotificationsValidationSchema = yup.object().shape({
  bookingEmail: nonEmptyStringOrNull().test(emailSchema),
})

export type VenueSettingsNotificationsFormValues = yup.InferType<
  typeof VenueSettingsNotificationsValidationSchema
>
