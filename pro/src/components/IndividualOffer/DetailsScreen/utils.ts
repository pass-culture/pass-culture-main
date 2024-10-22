import { FormikErrors } from 'formik'

import {
  CategoryResponseModel,
  GetIndividualOfferResponseModel,
  OfferStatus,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { showOptionsTree } from 'commons/core/Offers/categoriesSubTypes'
import { isOfferSynchronized } from 'commons/core/Offers/utils/typology'
import { SelectOption } from 'commons/custom_types/form'
import { trimStringsInObject } from 'commons/utils/trimStringsInObject'
import { computeVenueDisplayName } from 'repository/venuesService'

import { DEFAULT_DETAILS_FORM_VALUES } from './constants'
import { DetailsFormValues } from './types'

export const isSubCategoryCD = (subcategoryId: string): boolean => {
  return subcategoryId === SubcategoryIdEnum.SUPPORT_PHYSIQUE_MUSIQUE_CD
}

export const hasMusicType = (
  categoryId: string,
  subcategoryConditionalFields: string[]
): boolean => {
  // Books have a gtl_id field, other categories have a musicType field
  return categoryId !== 'LIVRE'
    ? subcategoryConditionalFields.includes('gtl_id')
    : subcategoryConditionalFields.includes('musicType')
}

export const buildCategoryOptions = (
  categories: CategoryResponseModel[]
): SelectOption[] =>
  categories
    .filter((category: CategoryResponseModel) => category.isSelectable)
    .map((category: CategoryResponseModel) => ({
      value: category.id,
      label: category.proLabel,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))

export const buildSubcategoryOptions = (
  subCategories: SubcategoryResponseModel[],
  categoryId: string
): SelectOption[] =>
  buildCategoryOptions(
    subCategories.filter(
      (subCategory: SubcategoryResponseModel) =>
        subCategory.categoryId === categoryId
    )
  )

export const buildShowSubTypeOptions = (showType: string): SelectOption[] => {
  if (showType === DEFAULT_DETAILS_FORM_VALUES.showType) {
    return []
  }

  const selectedShowTypeChildren = showOptionsTree.find(
    (showTypeOption) => showTypeOption.code === parseInt(showType)
  )?.children

  if (!selectedShowTypeChildren) {
    return []
  }

  return selectedShowTypeChildren
    .map((data) => ({
      value: data.code.toString(),
      label: data.label,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
}

export const completeSubcategoryConditionalFields = (
  subcategory?: SubcategoryResponseModel
): string[] => [
  ...new Set(subcategory?.conditionalFields),
  ...(subcategory?.isEvent ? ['durationMinutes'] : []),
]

type OnCategoryChangeProps = {
  readOnlyFields: string[]
  categoryId: string
  subcategories: SubcategoryResponseModel[]
  setFieldValue: (
    field: string,
    value: any,
    shouldValidate?: boolean | undefined
  ) => Promise<void | FormikErrors<DetailsFormValues>>
  onSubcategoryChange: (p: OnSubcategoryChangeProps) => Promise<void>
  subcategoryConditionalFields: string[]
  setIsEvent?: (isEvent: boolean | null) => void
}

export const onCategoryChange = async ({
  categoryId,
  readOnlyFields,
  subcategories,
  setFieldValue,
  onSubcategoryChange,
  subcategoryConditionalFields,
  setIsEvent,
}: OnCategoryChangeProps) => {
  if (readOnlyFields.includes('subcategoryId')) {
    return
  }
  const newSubcategoryOptions = buildSubcategoryOptions(
    subcategories,
    categoryId
  )
  const subcategoryId =
    newSubcategoryOptions.length === 1
      ? String(newSubcategoryOptions[0].value)
      : DEFAULT_DETAILS_FORM_VALUES.subcategoryId
  await setFieldValue('subcategoryId', subcategoryId, false)
  await onSubcategoryChange({
    newSubCategoryId: subcategoryId,
    subcategories,
    setFieldValue,
    subcategoryConditionalFields,
    setIsEvent,
  })
}

type OnSubcategoryChangeProps = {
  newSubCategoryId: string
  subcategories: SubcategoryResponseModel[]
  setFieldValue: (
    field: string,
    value: any,
    shouldValidate?: boolean | undefined
  ) => Promise<void | FormikErrors<DetailsFormValues>>
  subcategoryConditionalFields: string[]
  setIsEvent?: (isEvent: boolean | null) => void
}

export const onSubcategoryChange = async ({
  newSubCategoryId,
  subcategories,
  setFieldValue,
  subcategoryConditionalFields,
  setIsEvent,
}: OnSubcategoryChangeProps) => {
  const newSubcategory = subcategories.find(
    (subcategory) => subcategory.id === newSubCategoryId
  )

  if (setIsEvent) {
    setIsEvent(newSubcategory?.isEvent ?? null)
  }

  const newSubcategoryConditionalFields =
    completeSubcategoryConditionalFields(newSubcategory)
  await setFieldValue(
    'subcategoryConditionalFields',
    newSubcategoryConditionalFields
  )

  if (newSubcategoryConditionalFields === subcategoryConditionalFields) {
    return
  }

  const fieldsToReset = subcategoryConditionalFields.filter(
    (field: string) => !newSubcategoryConditionalFields.includes(field)
  )
  fieldsToReset.forEach(async (field: string) => {
    if (field in DEFAULT_DETAILS_FORM_VALUES) {
      await setFieldValue(
        field,
        DEFAULT_DETAILS_FORM_VALUES[
          field as keyof typeof DEFAULT_DETAILS_FORM_VALUES
        ]
      )
    }
  })
}

export const buildVenueOptions = (
  venues: VenueListItemResponseModel[],
  areSuggestedCategoriesEnabled: boolean
) => {
  let venueOptions = venues
    .filter((venue) => !areSuggestedCategoriesEnabled || !venue.isVirtual)
    .map((venue) => ({
      value: venue.id.toString(),
      label: computeVenueDisplayName(venue),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  if (venueOptions.length > 1) {
    venueOptions = [
      { value: '', label: 'Sélectionner le partenaire' },
      ...venueOptions,
    ]
  }

  return venueOptions
}

type SetDefaultInitialValuesProps = {
  filteredVenues: VenueListItemResponseModel[]
  areSuggestedSubcategoriesUsed: boolean
}

export function setDefaultInitialValues({
  filteredVenues,
  areSuggestedSubcategoriesUsed,
}: SetDefaultInitialValuesProps): DetailsFormValues {
  let venueId = ''

  const venues = areSuggestedSubcategoriesUsed
    ? filteredVenues.filter((v) => !v.isVirtual)
    : filteredVenues

  if (venues.length === 1) {
    venueId = String(venues[0].id)
  } else if (venues.length === 0 && filteredVenues.length > 0) {
    venueId = String(filteredVenues[0].id)
  }

  return {
    ...DEFAULT_DETAILS_FORM_VALUES,
    venueId,
  }
}

type SetDefaultInitialValuesFromOfferProps = {
  offer: GetIndividualOfferResponseModel
  subcategories: SubcategoryResponseModel[]
}

export function setDefaultInitialValuesFromOffer({
  offer,
  subcategories,
}: SetDefaultInitialValuesFromOfferProps): DetailsFormValues {
  const subcategory = subcategories.find(
    (subcategory: SubcategoryResponseModel) =>
      subcategory.id === offer.subcategoryId
  )

  if (subcategory === undefined) {
    throw Error('La categorie de l’offre est introuvable')
  }

  const ean = offer.extraData?.ean ?? DEFAULT_DETAILS_FORM_VALUES.ean

  return {
    ...DEFAULT_DETAILS_FORM_VALUES,
    name: offer.name,
    description: offer.description ?? DEFAULT_DETAILS_FORM_VALUES.description,
    venueId: String(offer.venue.id),
    categoryId: subcategory.categoryId,
    subcategoryId: offer.subcategoryId,
    showType: offer.extraData?.showType ?? DEFAULT_DETAILS_FORM_VALUES.showType,
    showSubType:
      offer.extraData?.showSubType ?? DEFAULT_DETAILS_FORM_VALUES.showSubType,
    subcategoryConditionalFields:
      completeSubcategoryConditionalFields(subcategory),
    durationMinutes: offer.durationMinutes
      ? deSerializeDurationMinutes(offer.durationMinutes)
      : DEFAULT_DETAILS_FORM_VALUES.durationMinutes,
    ean,
    visa: offer.extraData?.visa ?? DEFAULT_DETAILS_FORM_VALUES.visa,
    gtl_id: offer.extraData?.gtl_id ?? DEFAULT_DETAILS_FORM_VALUES.gtl_id,
    speaker: offer.extraData?.speaker ?? DEFAULT_DETAILS_FORM_VALUES.speaker,
    author: offer.extraData?.author ?? DEFAULT_DETAILS_FORM_VALUES.author,
    performer:
      offer.extraData?.performer ?? DEFAULT_DETAILS_FORM_VALUES.performer,
    stageDirector:
      offer.extraData?.stageDirector ??
      DEFAULT_DETAILS_FORM_VALUES.stageDirector,
    productId:
      offer.productId?.toString() ?? DEFAULT_DETAILS_FORM_VALUES.productId,
  }
}

export function deSerializeDurationMinutes(durationMinute: number): string {
  const hours = Math.floor(durationMinute / 60)
  const minutes = (durationMinute % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

export const serializeDurationMinutes = (
  durationHour: string
): number | undefined => {
  /* istanbul ignore next: DEBT, TO FIX */
  if (durationHour.trim().length === 0) {
    return undefined
  }

  /* istanbul ignore next: DEBT, TO FIX */
  const [hours, minutes] = durationHour
    .split(':')
    .map((s: string) => parseInt(s, 10))

  return minutes + hours * 60
}

export function setFormReadOnlyFields(
  offer: GetIndividualOfferResponseModel | null,
  isProductBased?: boolean
): string[] {
  if (isProductBased && offer === null) {
    const editableFields = ['venueId']

    return Object.keys(DEFAULT_DETAILS_FORM_VALUES).filter(
      (field) => !editableFields.includes(field)
    )
  }

  if (isProductBased && offer !== null) {
    return Object.keys(DEFAULT_DETAILS_FORM_VALUES)
  }

  if (offer === null) {
    return []
  }

  if ([OfferStatus.REJECTED, OfferStatus.PENDING].includes(offer.status)) {
    return Object.keys(DEFAULT_DETAILS_FORM_VALUES)
  }

  if (isOfferSynchronized(offer)) {
    return Object.keys(DEFAULT_DETAILS_FORM_VALUES)
  }

  return ['categoryId', 'subcategoryId', 'venueId']
}

export const serializeExtraData = (formValues: DetailsFormValues) => {
  return trimStringsInObject({
    author: formValues.author,
    gtl_id: formValues.gtl_id,
    performer: formValues.performer,
    showType: formValues.showType,
    showSubType: formValues.showSubType,
    speaker: formValues.speaker,
    stageDirector: formValues.stageDirector,
    visa: formValues.visa,
    ean: formValues.ean,
  })
}

type PostPayload = {
  description?: string | null
  durationMinutes?: number
  extraData?: Record<string, unknown>
  name: string
  subcategoryId: string
  venueId: number
  productId?: number
}

export function serializeDetailsPostData(
  formValues: DetailsFormValues
): PostPayload {
  return trimStringsInObject({
    name: formValues.name,
    subcategoryId: formValues.subcategoryId,
    venueId: Number(formValues.venueId),
    description: formValues.description,
    durationMinutes: serializeDurationMinutes(formValues.durationMinutes ?? ''),
    extraData: serializeExtraData(formValues),
    productId: formValues.productId ? Number(formValues.productId) : undefined,
  })
}

type PatchPayload = {
  description?: string | null
  durationMinutes?: number
  extraData?: Record<string, unknown>
  name: string
  subcategoryId: string
}

export function serializeDetailsPatchData(
  formValues: DetailsFormValues
): PatchPayload {
  return {
    name: formValues.name,
    subcategoryId: formValues.subcategoryId,
    description: formValues.description,
    durationMinutes: serializeDurationMinutes(formValues.durationMinutes ?? ''),
    extraData: serializeExtraData(formValues),
  }
}
