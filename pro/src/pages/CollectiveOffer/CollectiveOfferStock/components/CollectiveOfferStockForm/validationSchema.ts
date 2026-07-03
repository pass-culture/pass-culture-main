import { isAfter, isBefore, isSameDay, startOfToday } from 'date-fns'
import * as yup from 'yup'

import {
  type CollectiveAdditionalFeeModel,
  CollectiveAdditionalFeeType,
} from '@/apiClient/v1'
import { isDateValid } from '@/commons/utils/date'
import { nonEmptyStringOrNull } from '@/commons/utils/yup/nonEmptyStringOrNull'

import { computePriceForStock } from '../utils/computePriceForStock'
import {
  MAX_NUMBER_OF_TEACHERS,
  MAX_NUMBER_OF_TICKETS,
  MAX_PRICE,
} from '../utils/constants'
import { getMaxEndDateInSchoolYear } from '../utils/getMaxEndDateInSchoolYear'

function isPriceUnderMaxPrice(
  servicePrice: number | null,
  collectiveAdditionalFees: CollectiveAdditionalFeeModel[]
) {
  const price = computePriceForStock(servicePrice, collectiveAdditionalFees)
  // The first condition is tested by the `servicePrice.max()` test
  return (servicePrice ?? 0) > MAX_PRICE || price <= MAX_PRICE
}

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
      .integer('Nombre entier attendu')
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
      .integer('Nombre entier attendu')
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
    servicePrice: yup
      .number()
      .nullable()
      .transform((value) => (Number.isNaN(value) ? null : value))
      .defined()
      .min(0, 'Nombre positif attendu')
      .max(
        MAX_PRICE,
        `Le tarif de la prestation ne doit pas dépasser ${MAX_PRICE} €`
      )
      .test(
        'max-total-price',
        `Le prix total ne doit pas dépasser ${MAX_PRICE} €`,
        (servicePrice, { parent }) =>
          isPriceUnderMaxPrice(
            servicePrice,
            parent.collectiveAdditionalFees ?? []
          )
      )
      .required('Le tarif de la prestation est obligatoire'),
    hasAdditionalFees: yup.boolean().required('Veuillez choisir une option'),
    collectiveAdditionalFees: yup
      .array()
      .of(
        yup.object({
          type: yup
            .string()
            .oneOf(
              Object.values(CollectiveAdditionalFeeType),
              'Type de frais annexe invalide'
            )
            .required('Le type de frais annexe est obligatoire'),
          amount: yup
            .number()
            .nullable()
            .transform((value) => (Number.isNaN(value) ? null : value))
            .min(0.01, 'Le prix du frais annexe doit être supérieur à 0.01')
            .required('Le prix du frais annexe est obligatoire'),
          label: nonEmptyStringOrNull().when('type', {
            is: CollectiveAdditionalFeeType.OTHER,
            then: (schema) =>
              schema.required('Veuillez préciser le type de frais'),
            otherwise: (schema) =>
              schema.max(0, 'Le label doit être vide pour ce type de frais'),
          }),
        })
      )
      .defined()
      .test(
        'max-total-price',
        `Le prix total ne doit pas dépasser ${MAX_PRICE} €`,
        (collectiveAdditionalFees, { parent }) =>
          isPriceUnderMaxPrice(
            parent.servicePrice,
            collectiveAdditionalFees ?? []
          )
      )
      .when('hasAdditionalFees', {
        is: true,
        then: (schema) =>
          schema.min(1, 'Ajoutez au moins un type de frais annexes'),
        otherwise: (schema) => schema.max(0),
      })
      .default([]),
  })

export type CollectiveOfferStockFormValues = yup.InferType<
  ReturnType<typeof generateValidationSchema>
>
