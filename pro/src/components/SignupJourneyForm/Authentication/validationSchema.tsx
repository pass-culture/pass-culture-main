import { openToPublicValidationSchema } from 'components/OpenToPublicToggle/validationSchema'
import * as yup from 'yup'

import { checkCoords } from '@/commons/utils/coords'
import { validationSchema as addressValidationSchema } from '@/ui-kit/form/AddressSelect/validationSchema'

export const validationSchema = (shouldHandleNotDiffusibleOfferer: boolean) => {
  // For the signup journey, we need to specifically extend the "coords" field because it ALSO depends on "isOpenToPublic"
  const extendedAddressValidationSchema = {
    ...addressValidationSchema,
    coords: yup
      .string()
      .trim()
      .when(['manuallySetAddress', 'isOpenToPublic'], {
        is: (manuallySetAddress: boolean, isOpenToPublic: 'true' | 'false') =>
          manuallySetAddress && isOpenToPublic === 'true',
        then: (schema) =>
          schema
            .required('Veuillez renseigner les coordonnées GPS')
            .test('coords', 'Veuillez respecter le format attendu', (value) =>
              checkCoords(value)
            ),
      }),
  }

  return yup
    .object()
    .shape({
      siret: yup.string().required(),
      name: yup.string().when([], (_, schema) => {
        if (shouldHandleNotDiffusibleOfferer) {
          return schema.nullable()
        }
        return schema.required()
      }),
      publicName: yup
        .string()
        .when([], (_, schema) => {
          if (shouldHandleNotDiffusibleOfferer) {
            return schema.required(
              'Veuillez renseigner un nom public pour votre structure'
            )
          }
          return schema
        })
        .nullable(),
      ...extendedAddressValidationSchema,
    })
    .concat(openToPublicValidationSchema)
}
