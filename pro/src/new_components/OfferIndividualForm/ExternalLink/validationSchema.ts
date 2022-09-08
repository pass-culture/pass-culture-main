import * as yup from 'yup'

import { offerFormUrlRegex } from 'core/shared'

const validationSchema = {
  externalTicketOfficeUrl: yup.string().test({
    name: 'externalTicketOfficeUrl',
    message: 'Veuillez renseigner une URL valide. Ex : https://exemple.com',
    test: (url?: string) =>
      url ? url.match(offerFormUrlRegex) !== null : true,
  }),
}

export default validationSchema
