import * as yup from 'yup'

// import { LangField } from 'apiClient/v1'

// type EuropeanFormBackValues = {
//   city?: string | null
//   country?: string | null
//   street?: string | null
//   latitude: number
//   longitude: number
//   zipcode?: string | null
//   currency?: string | null
//   date?: string | null
//   description?: LangField | null
//   externalUrl?: string | null
//   imageAlt?: LangField | null
//   imageUrl?: string | null
//   price: number
//   title?: LangField | null
// }

export type EuropeanFormFrontValues = {
  city?: string
  country?: string
  street?: string
  latitude?: number
  longitude?: number
  zipcode?: string | null
  currency?: string
  date?: string
  description?: string
  externalUrl?: string
  imageUrl?: string
  imageAlt?: string
  price?: number
  name: string
  autoTranslate?: boolean
}

const DEFAULT_EUROPEAN_FORM_VALUES: EuropeanFormFrontValues = {
  city: '',
  country: '',
  street: '',
  latitude: 0,
  longitude: 0,
  zipcode: '',
  currency: 'EUR',
  date: '',
  description: '',
  externalUrl: '',
  imageUrl: '',
  imageAlt: '',
  price: 0,
  name: '',
  autoTranslate: true,
}

export const setDefaultInitialValues = (): EuropeanFormFrontValues => {
  return DEFAULT_EUROPEAN_FORM_VALUES
}

// FIX ME: this regex is subject to backtracking which can lead to "catastrophic backtracking", high memory usage and slow performance
// we cannot use the yup url validation because we need to allow {} in the url to interpolate some data
const offerFormUrlRegex = new RegExp(
  /*eslint-disable-next-line no-useless-escape*/
  /^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)(([a-z0-9]+([\-\.\.-\.@_a-z0-9]+)*\.[a-z]{2,5})|((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.){3}(25[0-5]|(2[0-4]|1\d|[1-9]|)\d))(:[0-9]{1,5})?\S*?$/,
  'i'
)

const urlValidation = yup.string().when('isVenueVirtual', {
  is: (isVenueVirtual: boolean) => isVenueVirtual,
  then: (schema) =>
    schema
      .required('Veuillez renseigner une URL valide. Ex : https://exemple.com')
      .test({
        name: 'url',
        message: 'Veuillez renseigner une URL valide. Ex : https://exemple.com',
        test: (url?: string) =>
          url ? url.match(offerFormUrlRegex) !== null : true,
      }),
})

export const validationSchema = yup.object().shape({
  name: yup.string().max(90).required('Veuillez renseigner un titre'),
  description: yup.string(),
  externalUrl: urlValidation,
  imageUrl: urlValidation,
  imageAlt: yup.string(),
  price: yup
    .number()
    .typeError('Veuillez renseigner un prix')
    .min(0, 'Le prix ne peut pas être inferieur à 0€')
    .required('Veuillez renseigner un prix'),
})
