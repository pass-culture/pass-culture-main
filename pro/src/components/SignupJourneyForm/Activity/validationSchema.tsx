import parsePhoneNumberFromString from 'libphonenumber-js'
import type { ObjectSchema } from 'yup'
import * as yup from 'yup'

import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'
import { getActivities } from '@/commons/mappings/mappings'
import { objectKeys } from '@/commons/utils/object'
import type { ActivityFormValues } from '@/components/SignupJourneyForm/Activity/ActivityForm'

export const validationSchema = (
  notOpenToPublic: boolean
): ObjectSchema<ActivityFormValues> => {
  const activityTypeValuesOpenToPublic = objectKeys(
    getActivities('OPEN_TO_PUBLIC')
  )
  const activityTypeValuesNotOpenToPublic = objectKeys(
    getActivities('NOT_OPEN_TO_PUBLIC')
  )

  const activityValidator = notOpenToPublic
    ? yup
        .mixed<ActivityNotOpenToPublicType>()
        .oneOf(activityTypeValuesNotOpenToPublic, 'Activité non valide')
    : yup
        .mixed<ActivityOpenToPublicType>()
        .oneOf(activityTypeValuesOpenToPublic, 'Activité non valide')

  return yup.object().shape({
    activity: activityValidator.required(
      'Veuillez sélectionner une activité principale'
    ),
    culturalDomains: yup
      .array()
      .of(yup.string().required())
      .when([], (_, schema) => {
        if (notOpenToPublic) {
          return schema
            .required(
              'Veuillez sélectionner un ou plusieurs domaines d’activité'
            )
            .min(1, 'Veuillez sélectionner un ou plusieurs domaines d’activité')
        }
        return schema
      }),
    socialUrls: yup
      .array()
      .of(
        yup.object().shape({
          url: yup
            .string()
            .default('')
            .url(
              'Veuillez renseigner une URL valide. Ex : https://exemple.com'
            ),
        })
      )
      .required(),
    targetCustomer: yup
      .object()
      .test({
        name: 'is-one-true',
        message: 'Veuillez sélectionner au moins une option',
        test: (values: Record<string, boolean>): boolean =>
          Object.values(values).includes(true),
      })
      .shape({
        individual: yup.boolean().required(),
        educational: yup.boolean().required(),
      })
      .required('Veuillez sélectionner au moins une option'),
    phoneNumber: yup
      .string()
      .min(10, 'Veuillez renseigner au moins 10 chiffres')
      .required('Veuillez renseigner un numéro de téléphone')
      .max(20, 'Veuillez renseigner moins de 20 chiffres')
      .test(
        'isPhoneValid',
        'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678',
        // TODO (jm) : Create a standard util function that can be used here and everywhere else (other "validationSchema.ts" files that checks phone numbers format
        (value) => {
          if (!value) {
            return false
          }
          const phoneNumber = parsePhoneNumberFromString(value, 'FR')
          return phoneNumber?.isValid()
        }
      ),
  })
}
