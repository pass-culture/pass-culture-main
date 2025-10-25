import * as yup from 'yup'

import { SIRET_LENGTH, unhumanizeSiret } from '@/commons/utils/siren'

export const validationSchema = yup.object().shape({
  siret: yup
    .string()
    .required('Veuillez renseigner un SIRET')
    .test(
      'len',
      `Le SIRET doit comporter ${SIRET_LENGTH} caractères`,
      (siret) =>
        Boolean(siret) && unhumanizeSiret(siret).length === SIRET_LENGTH
    ),
})
