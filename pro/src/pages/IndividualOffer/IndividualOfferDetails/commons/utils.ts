import { computeVenueDisplayName } from 'repository/venuesService'

import {
  type ArtistOfferLinkResponseModel,
  type CategoryResponseModel,
  type GetIndividualOfferResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
  type SubcategoryResponseModel,
  type VenueListItemResponseModel,
} from '@/apiClient/v1'
import { showOptionsTree } from '@/commons/core/Offers/categoriesSubTypes'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import type { AccessibilityFormValues } from '@/commons/core/shared/types'
import type { SelectOption } from '@/commons/custom_types/form'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { getAccessibilityInfoFromVenue } from '@/commons/utils/getAccessibilityInfoFromVenue'
import type { Option } from '@/pages/AdageIframe/app/types'

import { DEFAULT_DETAILS_FORM_VALUES } from './constants'
import { deSerializeDurationMinutes } from './serializers'
import type {
  DetailsFormValues,
  SetDefaultInitialValuesFromOfferProps,
} from './types'

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
    (showTypeOption) => showTypeOption.code === parseInt(showType, 10)
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

// Ensures each artist type (author, performer, stage director) has at least one initial field.
export const getInitialArtistOfferLinks = (
  offerLinks: ArtistOfferLinkResponseModel[],
  defaultLinks: ArtistOfferLinkResponseModel[]
): ArtistOfferLinkResponseModel[] => {
  const existingArtistTypes = new Set(offerLinks.map((a) => a.artistType))

  const missingDefaults = defaultLinks.filter(
    (d) => !existingArtistTypes.has(d.artistType)
  )

  return [...offerLinks, ...missingDefaults]
}

export const completeSubcategoryConditionalFields = (
  subcategory?: SubcategoryResponseModel
) =>
  [
    ...new Set(subcategory?.conditionalFields),
    ...(subcategory?.isEvent ? ['durationMinutes'] : []),
  ] as (keyof DetailsFormValues)[]

export function filterAvailableVenues(
  venues: VenueListItemResponseModel[],
  isOfferVirtual: boolean | undefined = undefined
): VenueListItemResponseModel[] {
  const physicalVenues = venues.filter((v) => !v.isVirtual)

  if (isOfferVirtual !== false && physicalVenues.length === 0) {
    return venues
  }

  return physicalVenues
}

export function getVenuesAsOptions(
  venues: readonly VenueListItemResponseModel[]
): Option[] {
  return venues
    .map((v) => ({
      value: String(v.id),
      label: computeVenueDisplayName(v),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
}

export function getInitialValuesFromVenues(
  availableVenues: VenueListItemResponseModel[],
  isNewOfferCreationFlowFeatureActive: boolean
): DetailsFormValues {
  //  When there is only one venue available, we can automatically use this venue as the initially selected one.
  const onlyVenue =
    availableVenues.length === 1 ? availableVenues[0] : undefined
  const venueId = onlyVenue?.id.toString() ?? ''

  if (isNewOfferCreationFlowFeatureActive) {
    return {
      ...DEFAULT_DETAILS_FORM_VALUES,
      venueId,
      accessibility: getAccessibilityInfoFromVenue(onlyVenue).accessibility,
    }
  }

  return {
    ...DEFAULT_DETAILS_FORM_VALUES,
    venueId,
  }
}

export function getInitialValuesFromOffer({
  offer,
  subcategories,
  isNewOfferCreationFlowFeatureActive,
}: SetDefaultInitialValuesFromOfferProps): DetailsFormValues {
  const subcategory = subcategories.find(
    (subcategory: SubcategoryResponseModel) =>
      subcategory.id === offer.subcategoryId
  )
  assertOrFrontendError(subcategory, 'La categorie de l’offre est introuvable.')

  const ean = offer.extraData?.ean ?? DEFAULT_DETAILS_FORM_VALUES.ean
  const maybeAccessibility = isNewOfferCreationFlowFeatureActive
    ? { accessibility: getAccessibilityFormValuesFromOffer(offer) }
    : {}
  const maybeUrl = isNewOfferCreationFlowFeatureActive ? {} : { url: offer.url }

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
    artistOfferLinks: getInitialArtistOfferLinks(
      offer.artistOfferLinks,
      DEFAULT_DETAILS_FORM_VALUES.artistOfferLinks
    ),
    performer:
      offer.extraData?.performer ?? DEFAULT_DETAILS_FORM_VALUES.performer,
    stageDirector:
      offer.extraData?.stageDirector ??
      DEFAULT_DETAILS_FORM_VALUES.stageDirector,
    productId:
      offer.productId?.toString() ?? DEFAULT_DETAILS_FORM_VALUES.productId,
    ...maybeAccessibility,
    ...maybeUrl,
  }
}

export function getAccessibilityFormValuesFromOffer(
  offer: GetIndividualOfferResponseModel
): AccessibilityFormValues {
  const accessibilityBase = {
    audio: !!offer.audioDisabilityCompliant,
    mental: !!offer.mentalDisabilityCompliant,
    motor: !!offer.motorDisabilityCompliant,
    visual: !!offer.visualDisabilityCompliant,
  }
  const hasSomeAccessibility = Object.values(accessibilityBase).some((v) => v)

  return {
    ...accessibilityBase,
    none: !hasSomeAccessibility,
  }
}

export function getFormReadOnlyFields(
  offer: GetIndividualOfferResponseModel | null,
  hasSelectedProduct: boolean,
  isNewOfferCreationFlowFeatureActive: boolean
): string[] {
  const isNewOfferDraft = offer === null

  const allFieldsExceptAccessibility: string[] = Object.keys(
    DEFAULT_DETAILS_FORM_VALUES
  )
  const maybeAccessibilityFields = isNewOfferCreationFlowFeatureActive
    ? ['accessibility']
    : []

  const hasPendingOrRejectedStatus =
    offer && [OfferStatus.REJECTED, OfferStatus.PENDING].includes(offer.status)

  // An EAN search was performed, so the form is product based.
  // Multiple fields are read-only.
  if (isNewOfferDraft && hasSelectedProduct) {
    return allFieldsExceptAccessibility.filter((field) => field !== 'venueId')
  }

  if (isNewOfferDraft) {
    return []
  }

  if (hasPendingOrRejectedStatus) {
    return [...allFieldsExceptAccessibility, ...maybeAccessibilityFields]
  }

  if (hasSelectedProduct || isOfferSynchronized(offer)) {
    return allFieldsExceptAccessibility
  }

  return ['categoryId', 'subcategoryId', 'venueId']
}
