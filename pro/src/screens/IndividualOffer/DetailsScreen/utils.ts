import { FormikErrors } from 'formik'

import {
  CategoryResponseModel,
  GetIndividualOfferResponseModel,
  OfferStatus,
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

type OnSubcategoryChangeProps = {
  newSubCategoryId: string
  subcategories: SubcategoryResponseModel[]
  setFieldValue: (
    field: string,
    value: any,
    shouldValidate?: boolean | undefined
  ) => Promise<void | FormikErrors<DetailsFormValues>>
}

export const onSubcategoryChange = async ({
  newSubCategoryId,
  subcategories,
  setFieldValue,
}: OnSubcategoryChangeProps) => {
  const newSubcategory = subcategories.find(
    (subcategory) => subcategory.id === newSubCategoryId
  )

  const { subcategoryConditionalFields } =
    buildSubcategoryConditonalFields(newSubcategory)
  await setFieldValue(
    'subcategoryConditionalFields',
    subcategoryConditionalFields
  )
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

type setDefaultInitialValuesProps = {
  filteredVenues: VenueListItemResponseModel[]
}

export function setDefaultInitialValues({
  filteredVenues,
}: setDefaultInitialValuesProps): DetailsFormValues {
  let venueId = ''

  if (filteredVenues.length === 1) {
    venueId = String(filteredVenues[0].id)
  }

  return {
    ...DEFAULT_DETAILS_FORM_VALUES,
    venueId,
  }
}

type setDefaultInitialValuesFromOfferProps = {
  offer: GetIndividualOfferResponseModel
  subcategories: SubcategoryResponseModel[]
}

export function setDefaultInitialValuesFromOffer({
  offer,
  subcategories,
}: setDefaultInitialValuesFromOfferProps): DetailsFormValues {
  const subcategory = subcategories.find(
    (subcategory: SubcategoryResponseModel) =>
      subcategory.id === offer.subcategoryId
  )

  if (subcategory === undefined) {
    throw Error('La categorie de l’offre est introuvable')
  }

  return {
    ...DEFAULT_DETAILS_FORM_VALUES,
    name: offer.name,
    description: offer.description ?? DEFAULT_DETAILS_FORM_VALUES.description,
    venueId: String(offer.venue.id),
    categoryId: subcategory.categoryId,
    subcategoryId: offer.subcategoryId,
    showType: offer.extraData.showType ?? DEFAULT_DETAILS_FORM_VALUES.showType,
    showSubType:
      offer.extraData.showSubType ?? DEFAULT_DETAILS_FORM_VALUES.showSubType,
    subcategoryConditionalFields: [],
    durationMinutes: offer.durationMinutes
      ? serializeDurationHour(offer.durationMinutes)
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

export function serializeDurationHour(durationMinute: number): string {
  const hours = Math.floor(durationMinute / 60)
  const minutes = (durationMinute % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
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
