import * as yup from 'yup'

export const validationSchema = () =>
  yup.object().shape({
    isPleasant: yup.string().required('Veuillez renseignez ce champ'),
    isConvenient: yup.string().required('Veuillez renseignez ce champ'),
    comment: yup.string().max(500),
  })
