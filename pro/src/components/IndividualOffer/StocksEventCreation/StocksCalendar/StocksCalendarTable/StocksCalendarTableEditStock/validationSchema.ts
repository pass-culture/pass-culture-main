import { isBefore } from 'date-fns'
import * as yup from 'yup'

import { isDateValid, removeTime } from 'commons/utils/date'
import { MAX_STOCKS_QUANTITY } from 'components/IndividualOffer/StocksThing/validationSchema'

import { EditStockFormValues } from './StocksCalendarTableEditStock'

export const validationSchema = yup.object<EditStockFormValues>().shape({
  date: yup
    .string()
    .test(
      'is-future',
      'L’évènement doit être à venir',
      (value) => isDateValid(value) && new Date(value) > removeTime(new Date())
    )
    .required('La date est obligatoire.'),
  time: yup.string().required("L'horaire est obligatoire."),
  priceCategory: yup.string().required('Le tarif est obligatoire.'),
  bookingLimitDate: yup
    .string()
    .required('La date limite de réservation est obligatorie.')
    .test(
      'is-after-date',
      "La date limite de réservation ne peut être postérieure à la date de début de l'évènement",
      function (limitDate) {
        return !isBefore(this.parent.date, limitDate)
      }
    ),
  quantity: yup
    .number()
    .transform((value) => (Number.isNaN(value) ? undefined : value))
    .min(0, 'Veuillez indiquer une quantité positive')
    .max(
      MAX_STOCKS_QUANTITY,
      'Veuillez modifier la quantité. Celle-ci ne peut pas être supérieure à 1 million'
    ),
})
