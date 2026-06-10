import * as yup from 'yup'

import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'
import { getActivities } from '@/commons/mappings/mappings'
import { emailSchema } from '@/commons/utils/isValidEmail'
import { objectKeys } from '@/commons/utils/object'
import { nonEmptyStringOrNull } from '@/commons/utils/yup/nonEmptyStringOrNull'
import { phoneNumberSchema } from '@/commons/utils/yup/phoneNumberSchema'

import { getVolunteeringUrlError } from './getVolunteeringUrlError'

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

const activityTypeValuesOpenToPublic = objectKeys(
  getActivities('OPEN_TO_PUBLIC')
)
const activityTypeValuesNotOpenToPublic = objectKeys(
  getActivities('NOT_OPEN_TO_PUBLIC')
)

const VenueContactValidationSchema = yup.object().shape({
  email: nonEmptyStringOrNull().test(emailSchema),
  phoneNumber: phoneNumberSchema(),
  socialMedias: nonEmptyStringOrNull(),
  website: nonEmptyStringOrNull().url(
    'Veuillez renseigner une URL valide. Ex : https://exemple.com'
  ),
})

export const VenueEditionValidationSchema = yup
  .object()
  .shape({
    audioDisabilityCompliant: yup.boolean().nullable().default(null).defined(),
    activity: yup
      .mixed<ActivityOpenToPublicType | ActivityNotOpenToPublicType>()
      .nullable()
      .when(['isOpenToPublic'], {
        is: true,
        then: (schema) =>
          schema
            .oneOf(activityTypeValuesOpenToPublic, 'Activité non valide')
            .required('Veuillez renseigner ce champ'),
      })
      .when(['isOpenToPublic'], {
        is: false,
        then: (schema) =>
          schema
            .oneOf(activityTypeValuesNotOpenToPublic, 'Activité non valide')
            .required('Veuillez renseigner ce champ'),
      }),
    contact: VenueContactValidationSchema,
    culturalDomains: yup
      .array()
      .of(yup.string().required())
      .when('isOpenToPublic', {
        is: false,
        then: (schema) =>
          schema
            .required(
              'Veuillez sélectionner un ou plusieurs domaines d’activité'
            )
            .min(
              1,
              'Veuillez sélectionner un ou plusieurs domaines d’activité'
            ),
        otherwise: (schema) => schema,
      }),
    description: nonEmptyStringOrNull(),
    isAccessibilityAppliedOnAllOffers: yup.boolean().default(true).defined(),
    isOpenToPublic: yup
      .boolean()
      .default(true)
      .defined()
      .required('Veuillez sélectionner une option'),
    mentalDisabilityCompliant: yup.boolean().nullable().default(null).defined(),
    openingHours: yup
      .object()
      .nullable()
      .when('isOpenToPublic', {
        is: 'true',
        then: (schema) => schema.shape(openingHoursSchemaShape),
      }),
    visualDisabilityCompliant: yup.boolean().nullable().default(null).defined(),
    volunteeringUrl: nonEmptyStringOrNull().test({
      name: 'is-volunteering-url-valid',
      test(value) {
        const error = getVolunteeringUrlError(value || '')

        return error ? this.createError({ message: error }) : true
      },
    }),
  })
  .when('isOpenToPublic', {
    is: 'true',
    then: (schema) =>
      schema.test({
        name: 'is-one-true',
        message: 'Veuillez sélectionner au moins un critère d’accessibilité',
        test: isOneTrue,
      }),
  })

export type VenueEditionValidationSchema = yup.InferType<
  typeof VenueEditionValidationSchema
>
