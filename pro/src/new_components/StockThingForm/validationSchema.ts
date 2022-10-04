import * as yup from 'yup'

export const getValidationSchema = (today: Date) => {
  const validationSchema = {
    price: yup
      .number()
      .typeError('Veuillez entrer un prix valide')
      .moreThan(-1, 'Le prix ne peut pas être inferieur à 0€')
      .lessThan(300, 'Veuillez renseigner un prix inférieur à 300€')
      .required('Veuillez entrer un prix valide'),
    bookingLimitDatetime: yup
      .date()
      .nullable()
      .min(today, "Veuillez sélectionner une date à partir d'aujourd'hui"),
    quantity: yup
      .number()
      .typeError('Doit être un nombre')
      .moreThan(-1, 'Doit être positif'),
  }

  return yup.object().shape(validationSchema)
}
