import * as yup from 'yup'

import {
  isRidetStartingWithRid7,
  isSiretStartingWithSiren,
  RIDET_LENGTH,
  SIRET_LENGTH,
  validRidetWithPrefixLength,
  validSiretLength,
} from '@/commons/utils/siren'

import type { VenueSettingsFormContext } from '../../commons/types'

export const SiretOrCommentValidationSchema = yup.object().shape({
  siret: yup
    .string()
    .when(['$isCaledonian', '$siren', '$withSiret'], (vals, schema) => {
      const [isCaledonian, siren, withSiret] = vals as [
        VenueSettingsFormContext['isCaledonian'],
        VenueSettingsFormContext['siren'],
        VenueSettingsFormContext['withSiret'],
      ]

      if (!withSiret) {
        return schema
      }

      if (isCaledonian) {
        return schema
          .required('Veuillez renseigner un RIDET')
          .test(
            'len',
            `Le RIDET doit comporter ${RIDET_LENGTH} caractères`,
            (ridetWithPrefix) =>
              Boolean(ridetWithPrefix) &&
              validRidetWithPrefixLength(ridetWithPrefix)
          )
          .test(
            'correspondingToRid7',
            'Le code RIDET doit correspondre à un établissement de votre structure',
            (ridetWithPrefix) =>
              Boolean(ridetWithPrefix) &&
              isRidetStartingWithRid7(ridetWithPrefix, siren)
          )
      }

      return schema
        .required('Veuillez renseigner un SIRET')
        .test(
          'len',
          `Le SIRET doit comporter ${SIRET_LENGTH} caractères`,
          (siret) => Boolean(siret) && validSiretLength(siret)
        )
        .test(
          'correspondingToSiren',
          'Le code SIRET doit correspondre à un établissement de votre structure',
          (siret) => Boolean(siret) && isSiretStartingWithSiren(siret, siren)
        )
    }),
})
