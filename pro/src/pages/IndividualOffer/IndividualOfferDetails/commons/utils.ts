
import {
  CategoryResponseModel,
  GetIndividualOfferResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { showOptionsTree } from 'commons/core/Offers/categoriesSubTypes'
import { isOfferSynchronized } from 'commons/core/Offers/utils/typology'
import { SelectOption } from 'commons/custom_types/form'
import { trimStringsInObject } from 'commons/utils/trimStringsInObject'
import { computeVenueDisplayName } from 'repository/venuesService'

import { DEFAULT_DETAILS_FORM_VALUES } from './constants'
import { DetailsFormValues } from './types'

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

export const buildShowSubTypeOptions = (showType?: string): SelectOption[] => {
  if (showType === DEFAULT_DETAILS_FORM_VALUES.showType || !showType) {
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
) =>
  [
    ...new Set(subcategory?.conditionalFields),
    ...(subcategory?.isEvent ? ['durationMinutes'] : []),
  ] as (keyof DetailsFormValues)[]

export const formatVenuesOptions = (
  venues: VenueListItemResponseModel[],
  isOnline: boolean
) => {
  //  We want to display the virtual venues only if there are no physical venues available
  //  We also want to prevent selecting a virtual venue for a physical offer form
  const hasAtLeastOnePhysicalVenue = venues.some((v) => !v.isVirtual)
  return venues
    .filter((venue) =>
      hasAtLeastOnePhysicalVenue || !isOnline ? !venue.isVirtual : true
    )
    .map((venue) => ({
      value: venue.id.toString(),
      label: computeVenueDisplayName(venue),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
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
    url: offer.url,
  }
}

export function deSerializeDurationMinutes(durationMinute: number): string {
  const hours = Math.floor(durationMinute / 60)
  const minutes = (durationMinute % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

export function setFormReadOnlyFields(
  offer: GetIndividualOfferResponseModel | null,
  isProductBased?: boolean
): string[] {
  const allFields: string[] = Object.keys(DEFAULT_DETAILS_FORM_VALUES)
  const hasPendingOrRejectedStatus =
    offer && [OfferStatus.REJECTED, OfferStatus.PENDING].includes(offer.status)

  // Offer is still a draft / being created.
  if (offer === null) {
    // An EAS search was performed, so the form is product based.
    // Multiple fields are read-only.
    if (isProductBased) {
      const editableFields = ['venueId']

      return allFields.filter((field) => !editableFields.includes(field))
    }

    return []
  } else if (
    isProductBased ||
    isOfferSynchronized(offer) ||
    hasPendingOrRejectedStatus
  ) {
    return allFields
  } else {
    return ['categoryId', 'subcategoryId', 'venueId']
  }
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
    url: formValues.url,
  })
}

type PatchPayload = {
  description?: string | null
  durationMinutes?: number
  extraData?: Record<string, unknown>
  name: string
  subcategoryId: string
  url?: string | null
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
    url: formValues.url,
  }
}
