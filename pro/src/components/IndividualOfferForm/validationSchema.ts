import * as yup from 'yup'

import { validationSchema as accessibilitySchema } from './Accessibility'
import { validationSchema as categoriesSchema } from './Categories'
import { validationSchema as externalLinkSchema } from './ExternalLink'
import { getValidationSchema as informationsSchema } from './Informations'
import { validationSchema as notificationsSchema } from './Notifications'
import { validationSchema as usefulInformationsSchema } from './UsefulInformations'

export const getValidationSchema = (lastProvider?: string | null) =>
  yup.object().shape({
    ...categoriesSchema,
    ...informationsSchema(lastProvider),
    ...usefulInformationsSchema,
    ...accessibilitySchema,
    ...notificationsSchema,
    ...externalLinkSchema,
  })
