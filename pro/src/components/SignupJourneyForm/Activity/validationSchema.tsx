import parsePhoneNumberFromString from 'libphonenumber-js'
import type { ObjectSchema } from 'yup'
import * as yup from 'yup'

import type { ActivityFormValues } from '@/components/SignupJourneyForm/Activity/ActivityForm'

export const validationSchema = (
  shouldRequireCulturalDomains: boolean
): ObjectSchema<ActivityFormValues> =>
  yup.object().shape({
    venueTypeCode: yup
      .string()
      .required('Veuillez sélectionner une activité principale'),
    culturalDomains: yup
      .array()
      .of(yup.string().required())
      .when([], (_, schema) => {
        if (shouldRequireCulturalDomains) {
          return schema
            .required('Sélectionnez un ou plusieurs domaines d’activité')
            .min(1, 'Sélectionnez un ou plusieurs domaines d’activité')
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
          const isValid = phoneNumber?.isValid()
          if (!isValid) {
            return false
          }
          return true
        }
      ),
  })
