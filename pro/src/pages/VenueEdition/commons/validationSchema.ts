import * as yup from 'yup'

import { isPhoneValid } from '@/commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { emailSchema } from '@/commons/utils/isValidEmail'

const isOneTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

// biome-ignore lint/suspicious/noExplicitAny: Debt
const accessibilityTestAndShape = (schema: any) => {
  return schema
    .test({
      name: 'is-one-true',
      message: 'Veuillez sélectionner au moins un critère d’accessibilité',
      test: isOneTrue,
    })
    .shape({
      mental: yup.boolean(),
      audio: yup.boolean(),
      visual: yup.boolean(),
      motor: yup.boolean(),
      none: yup.boolean(),
    })
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

export const openingHoursSchemaShape = {
  MONDAY: openingHoursDaySchema,
  TUESDAY: openingHoursDaySchema,
  WEDNESDAY: openingHoursDaySchema,
  THURSDAY: openingHoursDaySchema,
  FRIDAY: openingHoursDaySchema,
  SATURDAY: openingHoursDaySchema,
  SUNDAY: openingHoursDaySchema,
}

export const getValidationSchema = ({
  isVenueActivityFeatureActive,
}: {
  isVenueActivityFeatureActive: boolean
}) => {
  return yup.object().shape({
    accessibility: yup.object().when('isOpenToPublic', {
      is: 'true',
      then: (schema) => accessibilityTestAndShape(schema),
      otherwise: (schema) => schema,
    }),
    email: yup.string().nullable().test(emailSchema),
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
    isOpenToPublic: yup
      .string()
      .nullable()
      .required('Veuillez renseigner ce champ'),
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
    ...(isVenueActivityFeatureActive
      ? {
          activity: yup
            .string()
            .nullable()
            .when('isOpenToPublic', {
              is: 'true',
              then: (schema) => schema.required('Veuillez renseigner ce champ'),
            }),
        }
      : {}),
  })
}
