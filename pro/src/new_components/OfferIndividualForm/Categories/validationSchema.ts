import * as yup from 'yup'

const validationSchema = {
  categoryId: yup.string().required('Veuillez séléctionner une catégorie'),
  subcategoryId: yup.string().when('categoryId', {
    is: (categoryId: string) => categoryId !== undefined,
    then: yup.string().required('Veuillez séléctionner une sous-catégorie'),
    otherwise: yup.string(),
  }),
}

export default validationSchema