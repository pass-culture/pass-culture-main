import * as yup from 'yup'

import { unhumanizeSiret } from 'core/Venue'
import siretApiValidate from 'ui-kit/form_rff/fields/SiretField/validators/siretApiValidate'

const generateSiretValidationSchema = (
  siren: string,
  isSiretValued: boolean
) => {
  const siretValidationSchema = {
    siret: yup
      .string()
      .required('Veuillez renseigner un SIRET')
      .test(
        'len',
        'Le SIRET doit comporter 14 caractères',
        siret => !!siret && unhumanizeSiret(siret).length === 14
      )
      .test(
        'correspondingToSiren',
        'Le code SIRET doit correspondre à un établissement de votre structure',
        siret => siret && unhumanizeSiret(siret).startsWith(siren)
      )
      .test(
        'apiSiretValid',
        'Le code SIRET saisi n’est pas valide',
        async siret => {
          const response = await siretApiValidate(siret || '')
          return !response
        }
      ),
  }

  const commentValidationSchema = {
    comment: yup.string().required('Veuillez renseigner un commentaire'),
  }

  /* istanbul ignore next */
  return yup
    .object()
    .shape(isSiretValued ? siretValidationSchema : commentValidationSchema)
}

export default generateSiretValidationSchema
