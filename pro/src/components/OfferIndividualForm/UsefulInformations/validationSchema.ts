import * as yup from 'yup'

import { offerFormUrlRegex } from 'core/shared'

import { validationSchema as ticketWithdrawalValidationSchema } from './TicketWithdrawal'
import { validationSchema as venueValidationSchema } from './Venue'

const validationSchema = {
  ...venueValidationSchema,
  ...ticketWithdrawalValidationSchema,
  url: yup.string().when('isVenueVirtual', {
    is: (isVenueVirtual: boolean) => isVenueVirtual,
    then: schema =>
      schema
        .required(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
        .test({
          name: 'url',
          message:
            'Veuillez renseigner une URL valide. Ex : https://exemple.com',
          test: (url?: string) =>
            url ? url.match(offerFormUrlRegex) !== null : true,
        }),
  }),
  bookingContact: yup.string().when('subCategoryFields', {
    is: (subCategoryFields: string[]) =>
      subCategoryFields.includes('bookingContact'),
    then: schema =>
      schema
        .required('Veuillez renseigner une adresse email')
        .email('Veuillez renseigner un email valide'),
  }),
}

export default validationSchema
