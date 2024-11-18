import * as yup from 'yup'

export const validationSchema = () =>
  yup.object().shape({
    userSatisfaction: yup.string().required('Veuillez renseigner ce champ'),
    userComment: yup.string().max(500),
  })
