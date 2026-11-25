import {
  DisplayableActivity,
  type GetIndividualOfferResponseModelV2,
  type GetVenueResponseModel,
  type OfferExtraDataV2,
} from '@/apiClient/v1'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { DEFAULT_DESCRIPTION_FORM_VALUES } from '@/pages/IndividualOfferV2/IndividualOfferV2Description/constants'

import { DEFAULT_DETAILS_FORM_VALUES } from '../../IndividualOffer/IndividualOfferDescription/components/DetailsForm/constants'
import { getInitialArtistOfferLinks } from '../../IndividualOffer/IndividualOfferDescription/components/DetailsForm/utils'
import type { DescriptionFormValues } from './validationSchemaV2'

export function getFormV2ReadOnlyFields(
  offer: GetIndividualOfferResponseModelV2 | null,
  venue: GetVenueResponseModel
): string[] {
  const isClosed = withVenueHelpers(venue).isClosed
  const isNewOfferDraft = offer === null

  const allFieldsExceptAccessibility: string[] = Object.keys(
    DEFAULT_DETAILS_FORM_VALUES
  )

  if (isClosed) {
    return [...allFieldsExceptAccessibility, 'accessibility']
  }

  if (isNewOfferDraft) {
    return []
  }

  if (offer && isOfferDisabled(offer)) {
    return [...allFieldsExceptAccessibility, 'accessibility']
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

  return []
}

export function getInitialValuesFromOfferV2(
  offer: GetIndividualOfferResponseModelV2
): DescriptionFormValues {
  const extraData = offer.extraData as OfferExtraDataV2

  return {
    ...DEFAULT_DESCRIPTION_FORM_VALUES,
    name: offer.name,
    hasCulturalOutreachClaim: offer.hasCulturalOutreachClaim,
    description:
      offer.description ?? DEFAULT_DESCRIPTION_FORM_VALUES.description,
    durationMinutes:
      offer.durationMinutes ?? DEFAULT_DESCRIPTION_FORM_VALUES.durationMinutes,
    visualDisabilityCompliant: offer.visualDisabilityCompliant ?? false,
    // Each field must have a defined default, otherwise react-hook-form flags the
    // form as dirty as soon as the (empty) input registers.
    extraData: Object.fromEntries(
      Object.entries(DEFAULT_DESCRIPTION_FORM_VALUES.extraData).map(
        ([key, defaultValue]) => [
          key,
          extraData?.[key as keyof OfferExtraDataV2] ?? defaultValue,
        ]
      )
    ),
    artistOfferLinks: getInitialArtistOfferLinks(
      offer.artistOfferLinks,
      DEFAULT_DESCRIPTION_FORM_VALUES.artistOfferLinks
    ),
  } as DescriptionFormValues
}
