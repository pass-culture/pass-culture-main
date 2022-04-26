import * as yup from 'yup'

export const validationSchema = {
  title: yup.string().max(90).required('Veuillez renseigner un titre'),
  description: yup.string().max(1000),
}
