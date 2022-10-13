import * as yup from 'yup'

export const getValidationSchema = (today: Date) => {
  const bookingLimitMinDate = today
  bookingLimitMinDate.setHours(0, 0, 0, 0)
  const validationSchema = {
    price: yup
      .number()
      .typeError('Veuillez renseigner un prix')
      .moreThan(-1, 'Le prix ne peut pas être inferieur à 0€')
      .max(300, 'Veuillez renseigner un prix inférieur à 300€')
      .required('Veuillez renseigner un prix'),
    bookingLimitDatetime: yup
      .date()
      .nullable()
      .min(
        bookingLimitMinDate,
        "Veuillez sélectionner une date à partir d'aujourd'hui"
      ),
    quantity: yup
      .number()
      .typeError('Doit être un nombre')
      .moreThan(-1, 'Doit être positif'),
  }

  return yup.object().shape(validationSchema)
}
