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
        (siret) => !!siret && valideSiretLength(siret)
      )
      .test('apiSiretVisible', 'Le SIRET n’est pas visible', async (siret) => {
        const response = await siretApiValidate(siret || '')
        const isInvisible =
          response ===
          'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles.'
        displayInvisibleSirenBanner(isInvisible)
        return !isInvisible
      })
      .test('apiSiretValid', 'Le SIRET n’existe pas', async (siret) => {
        const response = await siretApiValidate(siret || '')
        return !response
      }),
  })
