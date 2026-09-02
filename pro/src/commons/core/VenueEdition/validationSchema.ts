import { openToPublicValidationSchema } from 'components/OpenToPublicToggle/validationSchema'
import type { ObjectSchema } from 'yup'
import * as yup from 'yup'

import { emailSchema } from '@/commons/utils/isValidEmail'
import { phoneNumberSchema } from '@/commons/utils/yup/phoneNumberSchema'

import { getVolunteeringUrlError } from './getVolunteeringUrlError'
import type { VenueEditionFormValues } from './types'

const isOneTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

const volunteeringUrlSchema: yup.TestConfig<string | null | undefined> = {
  name: 'is-volunteering-url-valid',
  test(value) {
    const error = getVolunteeringUrlError(value || '')
    return error ? this.createError({ message: error }) : true
  },
}

const openingHoursDaySchema = yup
  .array()
  //  TODO  : Maybe there is an easier way to check for validations (having an array of array makes it complicated to read)
  //  The solution could be to have a global function for the whole array that keeps track of the global context
  .of(
    yup
      .array()
      .required()
      .of(
        yup
          .string()
          //  Custom tests are necessary to get the index of the required field
          .test('first-time-required', 'Heure obligatoire', function (value) {
            return Boolean(!this.path.endsWith('[0]') || value)
          })
          .test('second-time-required', 'Heure obligatoire', function (value) {
            return Boolean(!this.path.endsWith('[1]') || value)
          })
          .test(
            'first-time-before',
            'Plage horaire incohérente',
            function (value) {
              return (
                !value ||
                !this.parent[1] ||
                this.path.endsWith('[1]') ||
                value < this.parent[1]
              )
            }
          )
      )
  )
  .test(
    'second-span-first-time-after-first-span-second-time',
    'Plages horaires incompatibles',
    (value) =>
      !value?.[0]?.[0] ||
      !value?.[0]?.[1] ||
      !value?.[1]?.[0] ||
      !value?.[1]?.[1] ||
      value[0][1] < value[1][0]
  )

const openingHoursSchemaShape = {
  MONDAY: openingHoursDaySchema,
  TUESDAY: openingHoursDaySchema,
  WEDNESDAY: openingHoursDaySchema,
  THURSDAY: openingHoursDaySchema,
  FRIDAY: openingHoursDaySchema,
  SATURDAY: openingHoursDaySchema,
  SUNDAY: openingHoursDaySchema,
}

export const getValidationSchema = (): ObjectSchema<VenueEditionFormValues> => {
  return yup
    .object()
    .shape({
      description: yup.string(),
      isAccessibilityAppliedOnAllOffers: yup.boolean().default(true).defined(),
      accessibility: yup
        .object()
        .when('isOpenToPublic', {
          is: 'true',
          then: (schema) =>
            schema.test({
              name: 'is-one-true',
              message:
                'Veuillez sélectionner au moins un critère d’accessibilité',
              test: isOneTrue,
            }),
        })
        .shape({
          mental: yup.boolean().nullable().default(null),
          audio: yup.boolean().nullable().default(null),
          visual: yup.boolean().nullable().default(null),
          motor: yup.boolean().nullable().default(null),
          none: yup.boolean().nullable().default(null),
        }),
      email: yup.string().nullable().test(emailSchema),
      phoneNumber: phoneNumberSchema(),
      webSite: yup
        .string()
        .url('Veuillez renseigner une URL valide. Ex : https://exemple.com')
        .nullable(),
      openingHours: yup
        .object()
        .nullable()
        .when('isOpenToPublic', {
          is: 'true',
          then: (schema) => schema.shape(openingHoursSchemaShape),
        }),
      volunteeringUrl: yup.string().test(volunteeringUrlSchema).nullable(),
      withdrawalDetails: yup.string().nullable(),
    })
    .concat(openToPublicValidationSchema)
}
