import * as yup from 'yup'

import { validationSchema as accessibilitySchema } from './Accessibility'
import { validationSchema as categoriesSchema } from './Categories'
import { validationSchema as informationsSchema } from './Informations'
import { validationSchema as notificationsSchema } from './Notifications'
import { validationSchema as optionDuoSchema } from './OptionDuo'
import { validationSchema as usefulInformationsSchema } from './UsefulInformations'

export const validationSchema = yup.object().shape({
  ...informationsSchema,
  ...usefulInformationsSchema,
  ...categoriesSchema,
  ...accessibilitySchema,
  ...notificationsSchema,
  ...optionDuoSchema,
})
