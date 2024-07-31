import { FormikErrors } from 'formik'

import {
  CategoryResponseModel,
  GetIndividualOfferResponseModel,
  OfferStatus,
  PostOfferBodyModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { showOptionsTree } from 'core/Offers/categoriesSubTypes'
import { isOfferSynchronized } from 'core/Offers/utils/synchronization'
import { SelectOption } from 'custom_types/form'
import { computeVenueDisplayName } from 'repository/venuesService'

import { DEFAULT_DETAILS_FORM_VALUES } from './constants'
import { DetailsFormValues } from './types'

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

export const buildSubcategoryConditonalFields = (
  subcategory?: SubcategoryResponseModel
): {
  subcategoryConditionalFields: string[]
} => {
  const subcategoryConditionalFields = [
    ...new Set(subcategory?.conditionalFields),
  ]
  const isEvent = Boolean(subcategory?.isEvent)

  if (isEvent) {
    subcategoryConditionalFields.push('durationMinutes')
  }

  return { subcategoryConditionalFields }
}

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
}

export const onCategoryChange = async ({
  categoryId,
  readOnlyFields,
  subcategories,
  setFieldValue,
  onSubcategoryChange,
  subcategoryConditionalFields,
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
}

export const onSubcategoryChange = async ({
  newSubCategoryId,
  subcategories,
  setFieldValue,
  subcategoryConditionalFields,
}: OnSubcategoryChangeProps) => {
  const newSubcategory = subcategories.find(
    (subcategory) => subcategory.id === newSubCategoryId
  )

  const { subcategoryConditionalFields: newSubcategoryConditionalFields } =
    buildSubcategoryConditonalFields(newSubcategory)
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

export const buildVenueOptions = (venues: VenueListItemResponseModel[]) => {
  let venueOptions = venues
    .map((venue) => ({
      value: venue.id.toString(),
      label: computeVenueDisplayName(venue),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  if (venueOptions.length > 1) {
    venueOptions = [
      { value: '', label: 'Sélectionner un lieu' },
      ...venueOptions,
    ]
  }

  return venueOptions
}

type SetDefaultInitialValuesProps = {
  filteredVenues: VenueListItemResponseModel[]
}

export function setDefaultInitialValues({
  filteredVenues,
}: SetDefaultInitialValuesProps): DetailsFormValues {
  let venueId = ''

  if (filteredVenues.length === 1) {
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

  const { subcategoryConditionalFields } =
    buildSubcategoryConditonalFields(subcategory)

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
    subcategoryConditionalFields: subcategoryConditionalFields,
    durationMinutes: offer.durationMinutes
      ? deSerializeDurationMinutes(offer.durationMinutes)
      : DEFAULT_DETAILS_FORM_VALUES.durationMinutes,
    ean: offer.extraData?.ean ?? DEFAULT_DETAILS_FORM_VALUES.ean,
    visa: offer.extraData?.visa ?? DEFAULT_DETAILS_FORM_VALUES.visa,
    gtl_id: offer.extraData?.gtl_id ?? DEFAULT_DETAILS_FORM_VALUES.gtl_id,
    speaker: offer.extraData?.speaker ?? DEFAULT_DETAILS_FORM_VALUES.speaker,
    author: offer.extraData?.author ?? DEFAULT_DETAILS_FORM_VALUES.author,
    performer:
      offer.extraData?.performer ?? DEFAULT_DETAILS_FORM_VALUES.performer,
    stageDirector:
      offer.extraData?.stageDirector ??
      DEFAULT_DETAILS_FORM_VALUES.stageDirector,
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
  offer: GetIndividualOfferResponseModel | null
): string[] {
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

export const serializeExtraData = (
  formValues: DetailsFormValues
): PostOfferBodyModel['extraData'] => {
  const extraData: PostOfferBodyModel['extraData'] = {}
  if (formValues.author) {
    extraData.author = formValues.author
  }
  if (formValues.gtl_id) {
    extraData.gtl_id = formValues.gtl_id
  }
  if (formValues.performer) {
    extraData.performer = formValues.performer
  }
  if (formValues.ean) {
    extraData.ean = formValues.ean
  }
  if (formValues.showType) {
    extraData.showType = formValues.showType
  }
  if (formValues.showSubType) {
    extraData.showSubType = formValues.showSubType
  }
  if (formValues.speaker) {
    extraData.speaker = formValues.speaker
  }
  if (formValues.stageDirector) {
    extraData.stageDirector = formValues.stageDirector
  }
  if (formValues.visa) {
    extraData.visa = formValues.visa
  }

  return extraData
}

type Payload = {
  description?: string
  durationMinutes?: number
  extraData?: Record<string, unknown>
  name: string
  subcategoryId: string
  venueId: number
}

export function serializeDetailsData(formValues: DetailsFormValues): Payload {
  const payload: Payload = {
    name: formValues.name,
    subcategoryId: formValues.subcategoryId,
    venueId: Number(formValues.venueId),
  }
  if (formValues.description) {
    payload.description = formValues.description
  }
  if (formValues.durationMinutes) {
    payload.durationMinutes = serializeDurationMinutes(
      formValues.durationMinutes
    )
  }
  const serializedExtraData = serializeExtraData(formValues)
  if (Object.keys(serializedExtraData).length > 0) {
    payload.extraData = serializedExtraData
  }

  return payload
}
