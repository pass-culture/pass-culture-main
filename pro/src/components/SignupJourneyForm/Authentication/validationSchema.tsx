import * as yup from 'yup'

import { validationSchema as addressValidationSchema } from 'components/Address/validationSchema'

export const validationSchema = (isOpenToPublicEnabled: boolean) => {
  return yup.object().shape({
    siret: yup.string().required(),
    name: yup.string().required(),
    publicName: yup.string().nullable(),
    ...(isOpenToPublicEnabled
      ? {
          isOpenToPublic: yup
            .string()
            .required('Veuillez sélectionner un choix'),
        }
      : {}),
    ...addressValidationSchema,
  })
}
