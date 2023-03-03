import * as yup from 'yup'

import { valideSiretLength } from 'components/VenueForm/Informations/SiretOrCommentFields/validationSchema'
import siretApiValidate from 'ui-kit/form_rff/fields/SiretField/validators/siretApiValidate'

export const validationSchema = yup.object().shape({
  siret: yup
    .string()
    .required('Veuillez renseigner un SIRET')
    .test(
      'len',
      'Le SIRET doit comporter 14 caractères',
      siret => !!siret && valideSiretLength(siret)
    )
    .test('apiSiretValid', 'Le SIRET n’existe pas', async siret => {
      const response = await siretApiValidate(siret || '')
      return !response
    }),
})
