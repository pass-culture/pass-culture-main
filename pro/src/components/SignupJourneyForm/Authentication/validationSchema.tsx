import * as yup from 'yup'

import { validationSchema as addressValidationSchema } from 'ui-kit/form/AddressSelect/validationSchema'

export const validationSchema = () => {
  return yup.object().shape({
    siret: yup.string().required(),
    name: yup.string().required(),
    publicName: yup.string().nullable(),
    isOpenToPublic: yup.string().required('Veuillez sélectionner un choix'),
    ...addressValidationSchema,
  })
}
