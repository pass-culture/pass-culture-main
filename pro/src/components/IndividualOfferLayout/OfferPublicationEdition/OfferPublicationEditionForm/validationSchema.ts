import * as yup from 'yup'

import {
  bookingAllowedDateValidationSchema,
  bookingAllowedTimeValidationSchema,
  publicationDateValidationSchema,
  publicationTimeValidationSchema,
} from 'pages/IndividualOfferSummary/IndividualOfferSummary/components/EventPublicationForm/validationSchema'

export const validationSchema = yup.object().shape({
  publicationMode: yup.string<'now' | 'later'>().required().nullable(),
  publicationDate: yup.string().when('isPaused', {
    is: false,
    then: (schema) => publicationDateValidationSchema(schema),
  }),
  publicationTime: yup.string().when('isPaused', {
    is: false,
    then: (schema) => publicationTimeValidationSchema(schema),
  }),
  bookingAllowedMode: yup.string<'now' | 'later'>().required().nullable(),
  bookingAllowedDate: yup.string().when('isPaused', {
    is: false,
    then: (schema) => bookingAllowedDateValidationSchema(schema),
  }),
  bookingAllowedTime: yup.string().when('isPaused', {
    is: false,
    then: (schema) => bookingAllowedTimeValidationSchema(schema),
  }),
  isPaused: yup.boolean().required(),
})
