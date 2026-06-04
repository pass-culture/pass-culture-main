import { activityValidator } from 'commons/utils/yup/activity'
import type { ObjectSchema } from 'yup'
import * as yup from 'yup'

import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'
import { phoneNumberSchema } from '@/commons/utils/yup/phoneNumberSchema'
import type { ActivityFormValues } from '@/components/SignupJourneyForm/Activity/ActivityForm'

export const validationSchema = (
  notOpenToPublic: boolean
): ObjectSchema<ActivityFormValues> => {
  return yup.object().shape({
    activity: activityValidator(notOpenToPublic).required(
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
