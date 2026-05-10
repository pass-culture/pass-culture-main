import type { ObjectSchema } from 'yup'
import * as yup from 'yup'

import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'
import { getActivities } from '@/commons/mappings/mappings'
import { objectKeys } from '@/commons/utils/object'
import type { ActivityFormValues } from '@/components/SignupJourneyForm/Activity/ActivityForm'
import { phoneNumberSchema } from '@/ui-kit/form/PhoneNumberInput/commons/phoneNumberSchema'

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

    otherActivityComment: yup.string().when('activity', {
      is: (activity: ActivityOpenToPublicType | ActivityNotOpenToPublicType) =>
        activity === 'OTHER',
      then: (schema) =>
        schema.required('Veuillez préciser votre type d’activité'),
    }),

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
        yup.object({
          url: yup
            .string()
            .url('Veuillez renseigner une URL valide. Ex : https://exemple.com')
            .defined(),
        })
      )
      .test(
        'at-least-one-url',
        'Veuillez renseigner au moins une URL',
        (value) => (value ?? []).some((item) => Boolean(item.url.trim()))
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

    phoneNumber: phoneNumberSchema().required(
      'Veuillez renseigner un numéro de téléphone'
    ),
  })
}
