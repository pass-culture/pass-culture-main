import * as yup from 'yup'

import { TargetCustomerTypeEnum } from './constants'

export const validationSchema = yup.object().shape({
  venueType: yup.string().required('Veuillez sélectionner un type de lieu'),
  socialUrls: yup.array().of(yup.string()).nullable(),
  targetCustomer: yup
    .string()
    .oneOf(
      Object.values(TargetCustomerTypeEnum),
      'Vous devez cocher l’une des options ci-dessus'
    )
    .required('Vous devez cocher l’une des options ci-dessus'),
})
