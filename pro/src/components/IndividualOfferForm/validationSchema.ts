import * as yup from 'yup'

import { validationSchema as accessibilitySchema } from './Accessibility/validationSchema'
import { validationSchema as categoriesSchema } from './Categories/validationSchema'
import { getValidationSchema as informationsSchema } from './Informations/validationSchema'
import { validationSchema as notificationsSchema } from './Notifications/validationSchema'
import { validationSchema as offerLocationSchema } from './OfferLocation/validationSchema'
import { validationSchema as usefulInformationsSchema } from './UsefulInformations/validationSchema'

export const getValidationSchema = (
  lastProvider?: string | null,
  enableOfferLocationSchema = false
) =>
  yup.object().shape({
    ...categoriesSchema,
    ...informationsSchema(lastProvider),
    ...usefulInformationsSchema,
    ...accessibilitySchema,
    ...(enableOfferLocationSchema ? offerLocationSchema : {}),
    ...notificationsSchema,
  })
