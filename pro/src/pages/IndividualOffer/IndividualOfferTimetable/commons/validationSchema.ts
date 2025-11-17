import type { ObjectSchema } from 'yup'
import * as yup from 'yup'

import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import { nonEmptyStringOrNull } from '@/commons/utils/yup/nonEmptyStringOrNull'
import { openingHoursSchemaShape } from '@/pages/VenueEdition/commons/validationSchema'

import type { QuantityPerPriceCategoryForm } from '../components/StocksCalendar/form/types'
import { quantityPerPriceCategoriesSchema } from '../components/StocksCalendar/form/validationSchema'
import { areOpeningHoursEmpty } from './areOpeningHoursEmpty'
import { HasDateEnum, type IndividualOfferTimetableFormValues } from './types'

export const validationSchema: ObjectSchema<IndividualOfferTimetableFormValues> =
  yup.object().shape({
    timetableType: yup
      .string<IndividualOfferTimetableFormValues['timetableType']>()
      .required(),
    startDate: nonEmptyStringOrNull().when(['timetableType', 'hasStartDate'], {
      is: (
        timetableType: string,
        hasStartDate: IndividualOfferTimetableFormValues['hasStartDate']
      ) => timetableType === 'openingHours' && hasStartDate === HasDateEnum.YES,
      then: (schema) => schema.nonNullable('La date de début est obligatoire'),
    }),
    hasEndDate: yup
      .mixed<HasDateEnum>()
      .oneOf(Object.values(HasDateEnum))
      .required(),
    hasStartDate: yup
      .mixed<HasDateEnum>()
      .oneOf(Object.values(HasDateEnum))
      .required(),
    endDate: nonEmptyStringOrNull().when(['timetableType', 'hasEndDate'], {
      is: (
        timetableType: string,
        hasEndDate: IndividualOfferTimetableFormValues['hasEndDate']
      ) => timetableType === 'openingHours' && hasEndDate === HasDateEnum.YES,
      then: (schema) =>
        schema
          .nonNullable('La date de fin est obligatoire')
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
          yup
            .object()
            .nullable()
            .shape(openingHoursSchemaShape)
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
