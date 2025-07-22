import * as yup from 'yup'

import { SubcategoryResponseModel } from 'apiClient/v1'
import { CATEGORY_STATUS } from 'commons/core/Offers/constants'
import { AccessibilityFormValues } from 'commons/core/shared/types'

import { DetailsFormValues } from './types'

const eanValidation = yup
  .string()
  .matches(/^\d*$/, "L'EAN doit être composé de 13 chiffres")
  .test({
    message: "L'EAN doit être composé de 13 chiffres.",
    test: (ean) => !ean || ean.length === 13,
  })

const isAnyTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

// TODO: this regex is subject to backtracking which can lead to "catastrophic backtracking", high memory usage and slow performance
// we cannot use the yup url validation because we need to allow {} in the url to interpolate some data
const offerFormUrlRegex = new RegExp(
  /*eslint-disable-next-line no-useless-escape*/
  /^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)(([a-z0-9]+([-..-.@_a-z0-9]+)*\.[a-z]{2,5})|((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.){3}(25[0-5]|(2[0-4]|1\d|[1-9]|)\d))(:[0-9]{1,5})?\S*?$/,
  'i'
)

const commonValidationShape = {
  name: yup.string().trim().max(90).required('Veuillez renseigner un titre'),
  description: yup.string(),
  author: yup.string(),
  performer: yup.string(),
  ean: eanValidation,
  speaker: yup.string(),
  stageDirector: yup.string(),
  visa: yup.string(),
  eanSearch: yup.string(),
  productId: yup.string(),
  callId: yup.string(),
  subcategoryConditionalFields: yup.array().required(),
  durationMinutes: yup.string().when('subcategoryConditionalFields', {
    is: (subcategoryConditionalFields: string[]) =>
      subcategoryConditionalFields.includes('durationMinutes'),
    then: (schema) =>
      schema.matches(
        /^(([01]?[0-9]|2[0-3]):[0-5][0-9])?$/,
        'Veuillez entrer une durée sous la forme HH:MM (ex: 1:30 pour 1h30)'
      ),
  }),
  categoryId: yup.string().required('Veuillez sélectionner une catégorie'),
  subcategoryId: yup
    .string()
    .required('Veuillez sélectionner une sous-catégorie'),
  showType: yup.string().when('subcategoryConditionalFields', {
    is: (subcategoryConditionalFields: string[]) =>
      subcategoryConditionalFields.includes('showType'),
    then: (schema) =>
      schema.required('Veuillez sélectionner un type de spectacle'),
  }),
  showSubType: yup.string().when('subcategoryConditionalFields', {
    is: (subcategoryConditionalFields: string[]) =>
      subcategoryConditionalFields.includes('showType'),
    then: (schema) =>
      schema.required('Veuillez sélectionner un sous-type de spectacle'),
  }),
  gtl_id: yup.string().when(['subcategoryConditionalFields', 'categoryId'], {
    is: (subcategoryConditionalFields: string[], categoryId: string) => {
      return (
        subcategoryConditionalFields.includes('gtl_id') &&
        categoryId !== 'LIVRE'
      )
    },
    then: (schema) => schema.required('Veuillez sélectionner un genre musical'),
  }),
  venueId: yup.string().required('Veuillez sélectionner une structure'),
}

export const getValidationSchema = (isDigitalOffer: boolean) => {
  return yup.object<DetailsFormValues>().shape({
    ...commonValidationShape,
    accessibility: yup.mixed<any>().optional(), // `any` represents `undefined` here which is impossible to type via yup
    url: isDigitalOffer
      ? yup
          .string()
          .required(
            'Veuillez renseigner une URL valide. Ex : https://exemple.com'
          )
          .test({
            name: 'url',
            message:
              'Veuillez renseigner une URL valide. Ex : https://exemple.com',
            test: (url?: string) =>
              url ? url.match(offerFormUrlRegex) !== null : true,
          })
      : yup.string().nullable(),
  })
}

export const getValidationSchemaForNewOfferCreationFlow = (
  subcategories: SubcategoryResponseModel[]
) => {
  return yup.object<DetailsFormValues>().shape({
    ...commonValidationShape,
    accessibility: yup
      .object<AccessibilityFormValues>()
      .test({
        name: 'is-any-true',
        message: 'Veuillez sélectionner au moins un critère d’accessibilité',
        test: isAnyTrue,
      })
      .shape({
        mental: yup.boolean().required(),
        audio: yup.boolean().required(),
        visual: yup.boolean().required(),
        motor: yup.boolean().required(),
        none: yup.boolean().required(),
      })
      .required(),
    url: yup.string().when('subcategoryId', {
      is: (subcategoryId: string) => {
        if (!subcategoryId) {return false}
        const selectedSubcategory = subcategories.find(
          (sc) => sc.id === subcategoryId
        )

        return (
          !!selectedSubcategory &&
          selectedSubcategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE
        )
      },
      then: (schema) =>
        schema
          .matches(offerFormUrlRegex, {
            message:
              'Veuillez renseigner une URL valide. Ex : https://exemple.com',
            excludeEmptyString: true,
          })
          .required(
            'Veuillez renseigner une URL valide. Ex : https://exemple.com'
          ),
      otherwise: (schema) => schema.nullable(),
    }),
  })
}

export const eanSearchValidationSchema = yup.object().shape({
  eanSearch: eanValidation,
})
