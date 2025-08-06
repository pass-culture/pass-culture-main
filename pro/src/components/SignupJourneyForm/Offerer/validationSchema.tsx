import * as yup from 'yup'

import { unhumanizeSiret } from '@/commons/core/Venue/utils'

export const validationSchema = yup.object().shape({
  siret: yup
    .string()
    .required('Veuillez renseigner un SIRET')
    .test(
      'len',
      'Le SIRET doit comporter 14 caractères',
      (siret) => Boolean(siret) && unhumanizeSiret(siret).length === 14
    ),
})
