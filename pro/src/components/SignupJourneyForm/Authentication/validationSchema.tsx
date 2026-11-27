import { openToPublicValidationSchema } from 'components/OpenToPublicToggle/validationSchema'
import * as yup from 'yup'

import { checkCoords } from '@/commons/utils/coords'
import { validationSchema as addressValidationSchema } from '@/ui-kit/form/AddressSelect/validationSchema'

// The backend sets this text on `street` for non diffusible offerers
// Tis constant should always be sync with the NON_DISCLOSED_ADDRESS constant in the backend.
export const NON_DISCLOSED_ADDRESS_ALT_TEXT = 'Adresse non diffusée'

export const validationSchema = (shouldHandleNotDiffusibleOfferer: boolean) => {
  const extendedAddressValidationSchema = {
    ...addressValidationSchema,
    street: yup
      .string()
      .trim()
      .when(['isOpenToPublic'], {
        is: (isOpenToPublic: 'true' | 'false') => isOpenToPublic === 'true',
        then: (schema) =>
          schema.test(
            'street',
            'Pour accueillir du public, veuillez renseigner une adresse précise',
            (value) => value !== NON_DISCLOSED_ADDRESS_ALT_TEXT
          ),
      })
      .required('Veuillez renseigner une adresse postale'),
    // For the signup journey, we need to specifically extend the "coords" field because it ALSO depends on "isOpenToPublic"
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
