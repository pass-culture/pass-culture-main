import { isAfter, isBefore, isSameDay } from 'date-fns'
import * as yup from 'yup'

import { CollectiveOfferAllowedAction } from '@/apiClient/v1/new'
import { MAX_PRICE_DETAILS_LENGTH } from '@/commons/core/OfferEducational/constants'
import { isDateValid } from '@/commons/utils/date'

import { getMaxEndDateInSchoolYear } from './utils/getMaxEndDateInSchoolYear'

const todayAtMidnight = () => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

const isBookingDateBeforeStartDate = (
  bookingLimitDate: Date | null | undefined,
  parent: yup.TestContext['parent']
) => {
  if (!isDateValid(parent.startDate) || !isDateValid(bookingLimitDate)) {
    return true
  }

  return (
    isBefore(bookingLimitDate, parent.startDate) ||
    isSameDay(bookingLimitDate, parent.startDate)
  )
}

function isBookingDateAfterNow(bookingLimitDate: string | null | undefined) {
  if (!isDateValid(bookingLimitDate)) {
    return true
  }

  return !isBefore(bookingLimitDate, todayAtMidnight())
}

export const generateValidationSchema = (
  offerAllowedActions: CollectiveOfferAllowedAction[],
  initialPrice: number | null
) => {
  // can edit everything except dates, including price (increase and decrease)
  const canEditDetails = offerAllowedActions.includes(
    CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
  )

  // can edit price (only decrease), numberOfTickets and educationalPriceDetails
  const canEditDiscount = offerAllowedActions.includes(
    CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
  )

  // can edit dates (start / end / bookingLimit)
  const canEditDates = offerAllowedActions.includes(
    CollectiveOfferAllowedAction.CAN_EDIT_DATES
  )

  let totalPriceValidation = yup
    .number()
    .nullable()
    .transform((value) => (Number.isNaN(value) ? null : value))
    .min(0, 'Nombre positif attendu')
    .max(60000, 'Le prix ne doit pas dépasser 60 000€')
    .required('Le prix total TTC est obligatoire')

  if (canEditDiscount && !canEditDetails && initialPrice) {
    totalPriceValidation = totalPriceValidation.max(
      initialPrice,
      'Vous ne pouvez pas définir un prix plus élevé.'
    )
  }

  return yup.object().shape({
    startDate: yup
      .string()
      .required('La date de début est obligatoire')
      .when([], {
        is: () => canEditDates,
        then: (schema) =>
          schema.test(
            'is-after-today',
            "La date de l’évènement doit être supérieure à aujourd'hui",
            (startDate) => !isBefore(startDate, todayAtMidnight())
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
              (endDate) => !isBefore(endDate, todayAtMidnight())
            )
            .test(
              'is-same-year',
              'Les dates doivent être sur la même année scolaire',
              function (endDate) {
                return !isAfter(
                  endDate,
                  getMaxEndDateInSchoolYear(this.parent.startDate)
                )
              }
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
            message: "L'heure doit être postérieure à l'heure actuelle",
          }),
      }),
    numberOfTickets: yup
      .number()
      .transform((value) => (Number.isNaN(value) ? null : value))
      .min(1, 'Minimum 1 participant')
      .max(3000, 'Le nombre de participants ne doit pas dépasser 3000')
      .nullable()
      .required('Le nombre de participants est obligatoire'),
    totalPrice: totalPriceValidation,
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
              (bookingLimitDate, { parent }) =>
                isBookingDateBeforeStartDate(new Date(bookingLimitDate), parent)
            )
            .test(
              'is-after-today',
              'La date limite de réservation doit être égale ou postérieure à la date actuelle',
              (bookingLimitDate) =>
                !canEditDetails || isBookingDateAfterNow(bookingLimitDate)
            ),
      }),
    educationalPriceDetail: yup
      .string()
      .required('L’information sur le prix est obligatoire')
      .max(MAX_PRICE_DETAILS_LENGTH),
  })
}
