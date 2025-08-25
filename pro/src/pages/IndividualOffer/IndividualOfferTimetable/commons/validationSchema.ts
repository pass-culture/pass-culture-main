import * as yup from 'yup'

import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import { openingHoursSchema } from '@/pages/VenueEdition/validationSchema'

import type { QuantityPerPriceCategoryForm } from '../components/StocksCalendar/form/types'
import { quantityPerPriceCategoriesSchema } from '../components/StocksCalendar/form/validationSchema'
import { areOpeningHoursEmpty } from './areOpeningHoursEmpty'
import type { IndividualOfferTimetableFormValues } from './types'

export const validationSchema = yup
  .object<IndividualOfferTimetableFormValues>()
  .shape({
    timetableType: yup
      .string<IndividualOfferTimetableFormValues['timetableType']>()
      .required(),
    startDate: yup.string().when(['timetableType', 'hasStartDate'], {
      is: (
        timetableType: string,
        hasStartDate: IndividualOfferTimetableFormValues['hasStartDate']
      ) => timetableType === 'openingHours' && hasStartDate === 'yes',
      then: (schema) => schema.required('La date de début est obligatoire'),
    }),
    hasEndDate: yup
      .string<IndividualOfferTimetableFormValues['hasEndDate']>()
      .required(),
    hasStartDate: yup
      .string<IndividualOfferTimetableFormValues['hasStartDate']>()
      .required(),
    endDate: yup.string().when(['timetableType', 'hasEndDate'], {
      is: (
        timetableType: string,
        hasEndDate: IndividualOfferTimetableFormValues['hasEndDate']
      ) => timetableType === 'openingHours' && hasEndDate === 'yes',
      then: (schema) =>
        schema
          .required('La date de fin est obligatoire')
          .test(
            'is-after-start',
            'La date de fin ne peut pas être antérieure à la date de début',
            function (endDate) {
              return !this.parent.startDate || endDate >= this.parent.startDate
            }
          ),
    }),
    openingHours: yup
      .object<WeekdayOpeningHoursTimespans>()
      .when('timetableType', {
        is: 'openingHours',
        then: () =>
          openingHoursSchema
            .required('Les horaires d’ouverture sont obligatoires')
            .test(
              'has-at-least-one-day',
              'Les horaires d’ouverture sont obligatoires',
              (openingHours) => {
                return !areOpeningHoursEmpty(
                  openingHours as WeekdayOpeningHoursTimespans
                )
              }
            ),
      }),
    quantityPerPriceCategories: yup
      .array<QuantityPerPriceCategoryForm>()
      .when('timetableType', {
        is: 'openingHours',
        then: () => quantityPerPriceCategoriesSchema,
      }),
  })
