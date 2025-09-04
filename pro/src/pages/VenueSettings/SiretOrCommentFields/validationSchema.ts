import * as yup from 'yup'

import { unhumanizeSiret } from '@/commons/core/Venue/utils'

import type { VenueSettingsFormValues } from '../types'

export const valideSiretLength = (siret: string) =>
  unhumanizeSiret(siret).length === 14

export const isSiretStartingWithSiren = (
  siret: string,
  siren?: string | null
) =>
  siren !== null &&
  siren !== undefined &&
  unhumanizeSiret(siret).startsWith(siren)

export const generateSiretValidationSchema = (
  isVenueVirtual: boolean,
  isSiretValued: boolean,
  siren?: string | null,
  _initialSiret?: string
) => {
  const siretValidationSchema = {
    siret: isVenueVirtual
      ? yup.string()
      : yup
          .string()
          .required('Veuillez renseigner un SIRET')
          .test(
            'len',
            'Le SIRET doit comporter 14 caractères',
            (siret) => Boolean(siret) && valideSiretLength(siret)
          )
          .test(
            'correspondingToSiren',
            'Le code SIRET doit correspondre à un établissement de votre structure',
            (siret) => Boolean(siret) && isSiretStartingWithSiren(siret, siren)
          ),
  }

  const commentValidationSchema = {
    comment: isVenueVirtual
      ? yup.string()
      : yup.string().required('Veuillez renseigner un commentaire'),
  }

  /* istanbul ignore next */
  return yup
    .object<VenueSettingsFormValues>()
    .shape(isSiretValued ? siretValidationSchema : commentValidationSchema)
}
