import type { ObjectSchema } from 'yup'

import { yup } from '@/commons/utils/yup'
import {
  bookingAllowedDateValidationSchema,
  bookingAllowedTimeValidationSchema,
  publicationDateValidationSchema,
  publicationTimeValidationSchema,
} from '@/commons/utils/yup/offerPublicationSchema'

import type { PublicationFormValues } from './types'

export const validationSchema: ObjectSchema<PublicationFormValues> = yup
  .object()
  .shape({
    publicationMode: yup.string<'now' | 'later'>().required(),
    publicationDate: publicationDateValidationSchema(yup.string()),
    publicationTime: publicationTimeValidationSchema(yup.string()),
    bookingAllowedMode: yup.string<'now' | 'later'>().required(),
    bookingAllowedDate: bookingAllowedDateValidationSchema(yup.string()),
    bookingAllowedTime: bookingAllowedTimeValidationSchema(yup.string()),
  })
