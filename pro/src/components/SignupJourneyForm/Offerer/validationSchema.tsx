import * as yup from 'yup'

import { valideSiretLength } from 'pages/VenueCreation/SiretOrCommentFields/validationSchema'

export const validationSchema = yup.object().shape({
  siret: yup
    .string()
    .required('Veuillez renseigner un SIRET')
    .test(
      'len',
      'Le SIRET doit comporter 14 caractères',
      (siret) => !!siret && valideSiretLength(siret)
    ),
})
