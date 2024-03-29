import * as yup from 'yup'

import siretApiValidate from 'core/Venue/siretApiValidate'
import { valideSiretLength } from 'pages/VenueCreation/SiretOrCommentFields/validationSchema'

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
        (siret) => !!siret && valideSiretLength(siret)
      )
      .test(
        'apiSiretVisible',
        "Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public",
        async (siret) => {
          const response = await siretApiValidate(siret || '')
          const isInvisible =
            response ===
            'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles.'
          displayInvisibleSirenBanner(isInvisible)
          return !isInvisible
        }
      )
      .test('apiSiretValid', 'Le SIRET n’existe pas', async (siret) => {
        const response = await siretApiValidate(siret || '')
        return !response
      }),
  })
