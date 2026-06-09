import {
  type ArtistOfferLinkResponseModel,
  type CategoryResponseModel,
  type GetIndividualOfferResponseModel,
  SubcategoryIdEnum,
  type SubcategoryResponseModel,
} from '@/apiClient/v1'
import {
  DisplayableActivity,
  type GetVenueResponseModel,
} from '@/apiClient/v1/new'
import { showOptionsTree } from '@/commons/core/Offers/categoriesSubTypes'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import type { AccessibilityFormValues } from '@/commons/core/shared/types'
import type { SelectOption } from '@/commons/custom_types/form'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { getAccessibilityInfoFromVenue } from '@/commons/utils/getAccessibilityInfoFromVenue'

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
  return categoryId === 'LIVRE'
    ? subcategoryConditionalFields.includes('musicType')
    : subcategoryConditionalFields.includes('gtl_id')
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
    (showTypeOption) => showTypeOption.code === Number.parseInt(showType, 10)
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

export function getInitialValuesFromVenue(
  venue: GetVenueResponseModel
): DetailsFormValues {
  return {
    ...DEFAULT_DETAILS_FORM_VALUES,
    accessibility: getAccessibilityInfoFromVenue(venue).accessibility,
    venueId: venue.id.toString(),
  }
}

export function getInitialValuesFromOffer({
  offer,
  subcategories,
}: SetDefaultInitialValuesFromOfferProps): DetailsFormValues {
  const subcategory = subcategories.find(
    (subcategory: SubcategoryResponseModel) =>
      subcategory.id === offer.subcategoryId
  )
  assertOrFrontendError(subcategory, 'La categorie de l’offre est introuvable.')

  const ean = offer.extraData?.ean ?? DEFAULT_DETAILS_FORM_VALUES.ean

  return {
    ...DEFAULT_DETAILS_FORM_VALUES,
    name: offer.name,
    hasCulturalOutreachClaim: offer.hasCulturalOutreachClaim,
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
    accessibility: getAccessibilityFormValuesFromOffer(offer),
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
  const hasSomeAccessibility = Object.values(accessibilityBase).some(Boolean)

  return {
    ...accessibilityBase,
    none: !hasSomeAccessibility,
  }
}

export function getFormReadOnlyFields(
  offer: GetIndividualOfferResponseModel | null,
  hasSelectedProduct: boolean,
  venue: GetVenueResponseModel
): string[] {
  const isNewOfferDraft = offer === null

  const allFieldsExceptAccessibility: string[] = Object.keys(
    DEFAULT_DETAILS_FORM_VALUES
  )

  // An EAN search was performed, so the form is product based.
  // Multiple fields are read-only.
  if (isNewOfferDraft && hasSelectedProduct) {
    return allFieldsExceptAccessibility.filter((field) => field !== 'venueId')
  }

  if (isNewOfferDraft) {
    return []
  }

  if (offer && isOfferDisabled(offer)) {
    return [...allFieldsExceptAccessibility, 'accessibility']
  }

  if (hasSelectedProduct) {
    return allFieldsExceptAccessibility
  }

  if (isOfferSynchronized(offer)) {
    // (tcoudray-pass, 10/02/26)
    // To unblock the synchronization of EPNs we, for now,
    // authorize the edition of synchronized offers' name and description
    // when the venue is a MUSEUM
    if (venue.activity === DisplayableActivity.MUSEUM) {
      return allFieldsExceptAccessibility.filter(
        (field) =>
          field !== 'name' &&
          field !== 'description' &&
          field !== 'hasCulturalOutreachClaim'
      )
    }
    return allFieldsExceptAccessibility.filter(
      (field) => field !== 'hasCulturalOutreachClaim'
    )
  }

  return ['categoryId', 'subcategoryId', 'venueId']
}
