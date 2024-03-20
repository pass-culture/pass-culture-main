import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  price: yup
    .number()
    .min(0, 'Veuillez renseigner un prix de vente supérieur à zero')
    .required('Veuillez renseigner un prix de vente'),
  quantity: yup
    .number()
    .min(0, 'Veuillez renseigner un nombre de place supérieur à zero')
    .integer('Veillez renseigner un nombre de places valide'),
})
