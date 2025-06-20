import { QuantityPerPriceCategoryForm, RecurrenceDays } from './types'

export const INITIAL_QUANTITY_PER_PRICE_CATEGORY: QuantityPerPriceCategoryForm =
  {
    priceCategory: '',
  }

export const weekDays = [
  { label: 'Lundi', value: RecurrenceDays.MONDAY },
  { label: 'Mardi', value: RecurrenceDays.TUESDAY },
  { label: 'Mercredi', value: RecurrenceDays.WEDNESDAY },
  { label: 'Jeudi', value: RecurrenceDays.THURSDAY },
  { label: 'Vendredi', value: RecurrenceDays.FRIDAY },
  { label: 'Samedi', value: RecurrenceDays.SATURDAY },
  { label: 'Dimanche', value: RecurrenceDays.SUNDAY },
]
