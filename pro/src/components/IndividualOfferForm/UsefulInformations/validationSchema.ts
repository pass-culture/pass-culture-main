import * as yup from 'yup'

import { validationSchema as ticketWithdrawalValidationSchema } from './TicketWithdrawal/validationSchema'
import { validationSchema as venueValidationSchema } from './Venue/validationSchema'

// FIX ME: this regex is subject to backtracking which can lead to "catastrophic backtracking", high memory usage and slow performance
// we cannot use the yup url validation because we need to allow {} in the url to interpolate some data
const offerFormUrlRegex = new RegExp(
  /*eslint-disable-next-line no-useless-escape*/
  /^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)(([a-z0-9]+([\-\.\.-\.@_a-z0-9]+)*\.[a-z]{2,5})|((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.){3}(25[0-5]|(2[0-4]|1\d|[1-9]|)\d))(:[0-9]{1,5})?\S*?$/,
  'i'
)

export const validationSchema = {
  ...venueValidationSchema,
  ...ticketWithdrawalValidationSchema,
  url: yup.string().when('isVenueVirtual', {
    is: (isVenueVirtual: boolean) => isVenueVirtual,
    then: (schema) =>
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
    then: (schema) =>
      schema
        .required('Veuillez renseigner une adresse email')
        .email(
          'Veuillez renseigner un email valide, exemple : mail@exemple.com'
        )
        .test({
          name: 'organisationEmailNotPassCulture',
          message: 'Ce mail doit vous appartenir',
          test: (value) => !value.toLowerCase().endsWith('@passculture.app'),
        }),
  }),
}
