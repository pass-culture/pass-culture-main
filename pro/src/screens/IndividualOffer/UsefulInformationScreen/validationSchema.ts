import * as yup from 'yup'

import { WithdrawalTypeEnum } from 'apiClient/v1'

// FIX ME: this regex is subject to backtracking which can lead to "catastrophic backtracking", high memory usage and slow performance
// we cannot use the yup url validation because we need to allow {} in the url to interpolate some data
const offerFormUrlRegex = new RegExp(
  /*eslint-disable-next-line no-useless-escape*/
  /^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)(([a-z0-9]+([\-\.\.-\.@_a-z0-9]+)*\.[a-z]{2,5})|((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.){3}(25[0-5]|(2[0-4]|1\d|[1-9]|)\d))(:[0-9]{1,5})?\S*?$/,
  'i'
)

const isAnyTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

export const getValidationSchema = (subcategories: string[]) => {
  return yup.object().shape({
    withdrawalType: yup.string().when([], {
      is: () => subcategories.includes('withdrawalType'),
      then: (schema) =>
        schema
          .oneOf(Object.values(WithdrawalTypeEnum))
          .required('Veuillez sélectionner l’une de ces options'),
    }),
    withdrawalDelay: yup.string().when('withdrawalType', {
      is: (withdrawalType: WithdrawalTypeEnum) =>
        subcategories.includes('withdrawalDelay') &&
        [WithdrawalTypeEnum.BY_EMAIL, WithdrawalTypeEnum.ON_SITE].includes(
          withdrawalType
        ),
      then: (schema) =>
        schema.required('Vous devez choisir l’une des options ci-dessus'),
    }),
    url: yup.string().when('isVenueVirtual', {
      is: (isVenueVirtual: boolean) => isVenueVirtual,
      then: (schema) =>
        schema
          .required(
            'Veuillez renseigner une URL valide. Ex : https://exemple.com'
          )
          .test({
            name: 'url',
            message:
              'Veuillez renseigner une URL valide. Ex : https://exemple.com',
            test: (url?: string) =>
              url ? url.match(offerFormUrlRegex) !== null : true,
          }),
    }),
    bookingContact: yup.string().when([], {
      is: () => subcategories.includes('bookingContact'),
      then: (schema) =>
        schema
          .required('Veuillez renseigner une adresse email')
          .email(
            'Veuillez renseigner un email valide, exemple : mail@exemple.com'
          )
          .test({
            name: 'organisationEmailNotPassCulture',
            message: 'Ce mail doit vous appartenir',
            test: (value) => !value.toLowerCase().endsWith('@passculture.app'),
          }),
    }),
    accessibility: yup
      .object()
      .test({
        name: 'is-any-true',
        message: 'Veuillez sélectionner au moins un critère d’accessibilité',
        test: isAnyTrue,
      })
      .shape({
        mental: yup.boolean(),
        audio: yup.boolean(),
        visual: yup.boolean(),
        motor: yup.boolean(),
        none: yup.boolean(),
      }),
    bookingEmail: yup.string().when('receiveNotificationEmails', {
      is: (receiveNotificationEmails: boolean) => receiveNotificationEmails,
      then: (schema) =>
        schema
          .required('Veuillez renseigner une adresse email')
          .email(
            'Veuillez renseigner un email valide, exemple : mail@exemple.com'
          ),
    }),
  })
}
