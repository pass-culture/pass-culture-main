import * as yup from 'yup'

export const validationSchema = () =>
  yup.object().shape({
    userSatisfaction: yup.string(),
    userComment: yup
      .string()
      .max(500)
      .required('Veuillez renseigner un commentaire'),
  })
