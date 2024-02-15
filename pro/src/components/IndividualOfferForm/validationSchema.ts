import * as yup from 'yup'

import { validationSchema as accessibilitySchema } from './Accessibility'
import { getValidationSchema as categoriesSchema } from './Categories'
import { validationSchema as externalLinkSchema } from './ExternalLink'
import { getValidationSchema as informationsSchema } from './Informations'
import { validationSchema as notificationsSchema } from './Notifications'
import { validationSchema as usefulInformationsSchema } from './UsefulInformations'

export const getValidationSchema = (
  isTiteliveMusicGenreFeatureEnabled: boolean,
  lastProvider?: string | null
) =>
  yup.object().shape({
    ...categoriesSchema(isTiteliveMusicGenreFeatureEnabled),
    ...informationsSchema(lastProvider),
    ...usefulInformationsSchema,
    ...accessibilitySchema,
    ...notificationsSchema,
    ...externalLinkSchema,
  })
