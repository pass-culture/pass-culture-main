import * as yup from 'yup'

import { urlRegex } from 'core/shared'

export const validationSchema = yup.object().shape({
  collectiveDescription: yup.string(),
  collectiveStudents: yup.array(),
  collectiveWebsite: yup.string().test({
    name: 'matchWebsiteUrl',
    message: 'l’URL renseignée n’est pas valide',
    test: (url?: string) => (url ? url.match(urlRegex) !== null : true),
  }),
})
