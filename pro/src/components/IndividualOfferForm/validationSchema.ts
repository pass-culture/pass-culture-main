import * as yup from 'yup'

import { validationSchema as accessibilitySchema } from './Accessibility/validationSchema'
import { getValidationSchema as categoriesSchema } from './Categories/validationSchema'
import { validationSchema as externalLinkSchema } from './ExternalLink/validationSchema'
import { getValidationSchema as informationsSchema } from './Informations/validationSchema'
import { validationSchema as notificationsSchema } from './Notifications/validationSchema'
import { validationSchema as usefulInformationsSchema } from './UsefulInformations/validationSchema'

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
