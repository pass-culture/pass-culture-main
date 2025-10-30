import * as yup from 'yup'

import { validationSchema as addressValidationSchema } from '@/ui-kit/form/AddressSelect/validationSchema'

export const validationSchema = (shouldHandleNotDiffusibleOfferer: boolean) => {
  return yup.object().shape({
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
    isOpenToPublic: yup.string().required('Veuillez sélectionner une option'),
    ...addressValidationSchema,
  })
}
