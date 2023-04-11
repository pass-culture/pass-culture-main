import * as yup from 'yup'

import { unhumanizeSiret } from 'core/Venue'
import siretApiValidate from 'core/Venue/siretApiValidate'

export const valideSiretLength = (siret: string) =>
  unhumanizeSiret(siret).length === 14

export const isSiretStartingWithSiren = (siret: string, siren: string) =>
  unhumanizeSiret(siret).startsWith(siren)

const generateSiretValidationSchema = (
  siren: string,
  isSiretValued: boolean
) => {
  const siretValidationSchema = {
    siret: yup.string().when('isVenueVirtual', {
      is: false,
      then: schema =>
        schema
          .required('Veuillez renseigner un SIRET')
          .test(
            'len',
            'Le SIRET doit comporter 14 caractères',
            siret => !!siret && valideSiretLength(siret)
          )
          .test(
            'correspondingToSiren',
            'Le code SIRET doit correspondre à un établissement de votre structure',
            siret => siret && isSiretStartingWithSiren(siret, siren)
          )
          .test(
            'apiSiretValid',
            'Le code SIRET saisi n’est pas valide',
            async siret => {
              const response = await siretApiValidate(siret || '')
              return !response
            }
          ),
    }),
  }

  const commentValidationSchema = {
    comment: yup.string().when('isVenueVirtual', {
      is: false,
      then: schema => schema.required('Veuillez renseigner un commentaire'),
    }),
  }

  /* istanbul ignore next */
  return yup
    .object()
    .shape(isSiretValued ? siretValidationSchema : commentValidationSchema)
}

export default generateSiretValidationSchema
