import { isAfter, isBefore, isSameDay, startOfToday } from 'date-fns'
import * as yup from 'yup'

import { isDateValid } from '@/commons/utils/date'

import {
  MAX_NUMBER_OF_TEACHERS,
  MAX_NUMBER_OF_TICKETS,
} from '../utils/constants'
import { getMaxEndDateInSchoolYear } from '../utils/getMaxEndDateInSchoolYear'

export const generateValidationSchema = (canEditDates: boolean) =>
  yup.object().shape({
    startDate: yup
      .string()
      .required('La date de début est obligatoire')
      .when([], {
        is: () => canEditDates,
        then: (schema) =>
          schema.test(
            'is-after-today',
            "La date de l’évènement doit être supérieure à aujourd'hui",
            (startDate) => !isBefore(startDate, startOfToday())
          ),
      }),
    endDate: yup
      .string()
      .required('La date de fin est obligatoire')
      .when([], {
        is: () => canEditDates,
        then: (schema) =>
          schema
            .test(
              'is-after-today',
              "La date de l’évènement doit être supérieure à aujourd'hui",
              (endDate) => !isBefore(endDate, startOfToday())
            )
            .test(
              'is-same-year',
              'Les dates doivent être sur la même année scolaire',
              (endDate, { parent }) =>
                !isAfter(endDate, getMaxEndDateInSchoolYear(parent.startDate))
            ),
      }),
    eventTime: yup
      .string()
      .required('L’horaire est obligatoire')
      .when('startDate', {
        is: (startDate: string) =>
          isSameDay(new Date(startDate), new Date()) && canEditDates,
        then: (schema) =>
          schema.test({
            name: 'is-before-current-time',
            test: (eventTime: string) => {
              const date = new Date()
              const [hours, minutes] = eventTime.split(':')
              date.setHours(Number(hours))
              date.setMinutes(Number(minutes))

              return Date.now() < date.getTime()
            },
            message: "L'horaire doit être postérieur à l'heure actuelle",
          }),
      }),
    numberOfTickets: yup
      .number()
      .transform((value) => (Number.isNaN(value) ? null : value))
      .min(1, 'Minimum 1 élève')
      .max(
        MAX_NUMBER_OF_TICKETS,
        `Le nombre d'élèves ne doit pas dépasser ${MAX_NUMBER_OF_TICKETS}`
      )
      .nullable()
      .required("Le nombre d'élèves est obligatoire"),
    numberOfTeachers: yup
      .number()
      .transform((value) => (Number.isNaN(value) ? null : value))
      .min(0, 'Minimum 0 accompagnateur')
      .max(
        MAX_NUMBER_OF_TEACHERS,
        `Le nombre d'accompagnateurs ne doit pas dépasser ${MAX_NUMBER_OF_TEACHERS}`
      )
      .nullable()
      .required("Le nombre d'accompagnateurs est obligatoire"),
    bookingLimitDate: yup
      .string()
      .required('La date limite de réservation est obligatoire')
      .when([], {
        is: () => canEditDates,
        then: (schema) =>
          schema
            .test(
              'is-before-event',
              'La date limite de réservation doit être fixée au plus tard le jour de l’évènement',
              (bookingLimitDate, { parent }) => {
                if (
                  !isDateValid(parent.startDate) ||
                  !isDateValid(bookingLimitDate)
                ) {
                  return true
                }
                return !isAfter(bookingLimitDate, parent.startDate)
              }
            )
            .test(
              'is-after-today',
              'La date limite de réservation doit être égale ou postérieure à la date actuelle',
              (bookingLimitDate) => {
                if (!isDateValid(bookingLimitDate)) {
                  return true
                }
                return !isBefore(bookingLimitDate, startOfToday())
              }
            ),
      }),
  })

export type CollectiveOfferStockFormValues = yup.InferType<
  ReturnType<typeof generateValidationSchema>
>
