import * as yup from 'yup'

import { valideSiretLength } from 'components/VenueForm/Informations/SiretOrCommentFields/validationSchema'
import siretApiValidate from 'core/Venue/siretApiValidate'

export const validationSchema = (
  displayInvisibleSirenBanner: (showBanner: boolean) => void
) =>
  yup.object().shape({
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
        displayInvisibleSirenBanner(
          response ===
            'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles.'
        )
        return !response
      }),
  })
