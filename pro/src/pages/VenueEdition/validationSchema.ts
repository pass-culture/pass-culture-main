import * as yup from 'yup'

import { isPhoneValid } from 'core/shared/utils/validation'

import { Day } from './types'

const isOneTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

export const getValidationSchema = (validateAccessibility: boolean) =>
  yup.object().shape({
    accessibility: validateAccessibility
      ? yup
          .object()
          .test({
            name: 'is-one-true',
            message:
              'Veuillez sélectionner au moins un critère d’accessibilité',
            test: isOneTrue,
          })
          .shape({
            mental: yup.boolean(),
            audio: yup.boolean(),
            visual: yup.boolean(),
            motor: yup.boolean(),
            none: yup.boolean(),
          })
      : yup.object(),
    email: yup
      .string()
      .nullable()
      .email('Veuillez renseigner un email valide, exemple : mail@exemple.com'),
    phoneNumber: yup
      .string()
      .nullable()
      .test({
        name: 'is-phone-valid',
        message:
          'Veuillez entrer un numéro de téléphone valide, exemple : 612345678',
        test: (phone?: string | null) => {
          /* istanbul ignore next: DEBT, TO FIX */
          return phone ? isPhoneValid(phone) : true
        },
      }),
    webSite: yup
      .string()
      .url('Veuillez renseigner une URL valide. Ex : https://exemple.com')
      .nullable(),
    monday: yup.object().when('days', {
      is: (days: Day[]) => days.includes('monday'),
      then: (schema) => schema.shape(openingHoursValidationSchema),
    }),
    tuesday: yup.object().when('days', {
      is: (days: Day[]) => days.includes('tuesday'),
      then: (schema) => schema.shape(openingHoursValidationSchema),
    }),
    wednesday: yup.object().when('days', {
      is: (days: Day[]) => days.includes('wednesday'),
      then: (schema) => schema.shape(openingHoursValidationSchema),
    }),
    thursday: yup.object().when('days', {
      is: (days: Day[]) => days.includes('thursday'),
      then: (schema) => schema.shape(openingHoursValidationSchema),
    }),
    friday: yup.object().when('days', {
      is: (days: Day[]) => days.includes('friday'),
      then: (schema) => schema.shape(openingHoursValidationSchema),
    }),
    saturday: yup.object().when('days', {
      is: (days: Day[]) => days.includes('saturday'),
      then: (schema) => schema.shape(openingHoursValidationSchema),
    }),
    sunday: yup.object().when('days', {
      is: (days: Day[]) => days.includes('sunday'),
      then: (schema) => schema.shape(openingHoursValidationSchema),
    }),
  })

const openingHoursValidationSchema = {
  morningStartingHour: yup
    .string()
    .required('Veuillez renseigner une heure de début'),
  morningEndingHour: yup
    .string()
    .required('Veuillez renseigner une heure de fin')
    .when('morningStartingHour', (morningStartingHour, schema) => {
      return morningStartingHour[0]
        ? schema.test({
            test: (morningEndingHour: string) => {
              return compareHours(morningStartingHour[0], morningEndingHour)
            },
            message: "L'heure de fin doit être supérieure à l'heure de début",
          })
        : schema
    }),
  afternoonStartingHour: yup.string().when('isAfternoonOpen', {
    is: (isAfternoonOpen: boolean) => isAfternoonOpen,
    then: (schema) => schema.required('Veuillez renseigner une heure de début'),
  }),
  afternoonEndingHour: yup.string().when('isAfternoonOpen', {
    is: (isAfternoonOpen: boolean) => isAfternoonOpen,
    then: (schema) =>
      schema
        .required('Veuillez renseigner une heure de fin')
        .when('afternoonStartingHour', (afternoonStartingHour, schema) => {
          return afternoonStartingHour.length > 0
            ? schema.test({
                test: (afternoonEndingHour: string) => {
                  return compareHours(
                    afternoonStartingHour[0],
                    afternoonEndingHour
                  )
                },
                message:
                  "L'heure de fin doit être supérieure à l'heure de début",
              })
            : schema
        }),
  }),
}

function compareHours(start?: string, end?: string): boolean {
  if (!start || !end) {
    return false
  }

  const [startHours, startMinutes] = start.split(':').map(Number)
  const [endHours, endMinutes] = end.split(':').map(Number)

  const startDate = new Date()
  startDate.setHours(startHours || 0, startMinutes)

  const endDate = new Date()
  endDate.setHours(endHours || 0, endMinutes)

  return endDate > startDate
}
