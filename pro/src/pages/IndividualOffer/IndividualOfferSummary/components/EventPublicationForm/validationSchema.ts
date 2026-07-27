import type { ObjectSchema } from 'yup'

import { yup } from '@/commons/utils/yup'
import {
  bookingAllowedDateValidationSchema,
  bookingAllowedTimeValidationSchema,
  publicationDateValidationSchema,
  publicationTimeValidationSchema,
} from '@/commons/utils/yup/eventPublicationSchema'

import type { EventPublicationFormValues } from './types'

export const validationSchema: ObjectSchema<EventPublicationFormValues> = yup
  .object()
  .shape({
    publicationMode: yup.string<'now' | 'later'>().required(),
    publicationDate: publicationDateValidationSchema(yup.string()),
    publicationTime: publicationTimeValidationSchema(yup.string()),
    bookingAllowedMode: yup.string<'now' | 'later'>().required(),
    bookingAllowedDate: bookingAllowedDateValidationSchema(yup.string()),
    bookingAllowedTime: bookingAllowedTimeValidationSchema(yup.string()),
  })
