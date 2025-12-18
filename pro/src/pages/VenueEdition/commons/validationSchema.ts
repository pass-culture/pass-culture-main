import * as yup from 'yup'

import { isPhoneValid } from '@/commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { emailSchema } from '@/commons/utils/isValidEmail'

const isNotNullAndOneTrue = (values: Record<string, boolean> | null): boolean =>
  values !== null && Object.values(values).includes(true)

const openingHoursDaySchema = yup
  .array()
  .defined()
  .nullable()
  .default(null)
  //  TODO  : Maybe there is an easier way to check for validations (having an array of array makes it complicated to read)
  //  The solution could be to have a global function for the whole array that keeps track of the global context
  .of(
    yup
      .array()
      .defined()
      .required()
      .of(
        yup
          .string()
          .defined()
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

export const openingHoursSchemaShape = {
  MONDAY: openingHoursDaySchema.optional(),
  TUESDAY: openingHoursDaySchema.optional(),
  WEDNESDAY: openingHoursDaySchema.optional(),
  THURSDAY: openingHoursDaySchema.optional(),
  FRIDAY: openingHoursDaySchema.optional(),
  SATURDAY: openingHoursDaySchema.optional(),
  SUNDAY: openingHoursDaySchema.optional(),
}

export const accessibilityValidationSchema = yup.object({
  mental: yup.boolean().default(false),
  audio: yup.boolean().default(false),
  visual: yup.boolean().default(false),
  motor: yup.boolean().default(false),
  none: yup.boolean().default(false),
})

export const validationSchema = yup.object().shape({
  accessibility: accessibilityValidationSchema
    .nullable()
    .default(null)
    .defined()
    .when('isOpenToPublic', {
      is: 'true',
      then: (schema) =>
        schema.test({
          name: 'is-one-true',
          message: 'Veuillez sélectionner au moins un critère d’accessibilité',
          test: isNotNullAndOneTrue,
        }),
    }),
  email: yup.string().nullable().default(null).defined().test(emailSchema),
  description: yup.string().nullable().default(null).defined(),
  isAccessibilityAppliedOnAllOffers: yup.boolean().default(true).defined(),
  phoneNumber: yup
    .string()
    .nullable()
    .default(null)
    .defined()
    .test({
      name: 'is-phone-valid',
      message:
        'Veuillez entrer un numéro de téléphone valide, exemple : 612345678',
      test: (phone?: string | null) => {
        // istanbul ignore next: DEBT, TO FIX
        return phone ? isPhoneValid(phone) : true
      },
    }),
  isOpenToPublic: yup
    .string()
    .nullable()
    .default(null)
    .defined()
    .required('Veuillez renseigner ce champ'),
  webSite: yup
    .string()
    .url('Veuillez renseigner une URL valide. Ex : https://exemple.com')
    .nullable()
    .default(null)
    .defined(),
  openingHours: yup
    .object()
    .nullable()
    .default(null)
    .defined()
    .shape(openingHoursSchemaShape)
    .when(['isOpenToPublic', '$isVenueActivityFeatureActive'], {
      is: (isOpenToPublic: string, isVenueActivityFeatureActive: boolean) =>
        isOpenToPublic === 'true' && isVenueActivityFeatureActive === true,
      then: (schema) => schema,
    }),
  activity: yup
    .string()
    .nullable()
    .default(null)
    .defined()
    .when(['isOpenToPublic', '$isVenueActivityFeatureActive'], {
      is: (isOpenToPublic: string, isVenueActivityFeatureActive: boolean) =>
        isOpenToPublic === 'true' && isVenueActivityFeatureActive === true,
      then: (schema) => schema.required('Veuillez renseigner ce champ'),
    }),
})

export type VenueEditionFormValuesType = yup.InferType<typeof validationSchema>
