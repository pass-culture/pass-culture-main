import * as yup from 'yup'

import { offerFormUrlRegex } from 'core/shared'

import { validationSchema as ticketWithdrawalValidationSchema } from './TicketWithdrawal'
import { validationSchema as venueValidationSchema } from './Venue'

const validationSchema = {
  ...venueValidationSchema,
  ...ticketWithdrawalValidationSchema,
  url: yup.string().when('isVenueVirtual', {
    is: (isVenueVirtual: boolean) => isVenueVirtual,
    then: yup
      .string()
      .required('Veuillez renseigner une URL valide. Ex : https://exemple.com')
      .test({
        name: 'url',
        message: 'Veuillez renseigner une URL valide. Ex : https://exemple.com',
        test: (url?: string) =>
          url ? url.match(offerFormUrlRegex) !== null : true,
      }),
  }),
}

export default validationSchema
