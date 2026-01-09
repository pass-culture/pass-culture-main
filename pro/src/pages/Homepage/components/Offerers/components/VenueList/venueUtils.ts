import {
  DMSApplicationstatus,
  type GetOffererResponseModel,
  type GetOffererVenueResponseModel,
  type GetVenueResponseModel,
} from '@/apiClient/v1'
import { getLastCollectiveDmsApplication } from '@/commons/utils/getLastCollectiveDmsApplication'

export const getPhysicalVenuesFromOfferer = (
  offerer?: GetOffererResponseModel | null
): GetOffererVenueResponseModel[] =>
  offerer?.managedVenues?.filter((venue) => !venue.isVirtual) ?? []

export const hasOffererAtLeastOnePhysicalVenue = (
  offerer?: GetOffererResponseModel | null
): boolean =>
  offerer?.managedVenues?.some((venue) => !venue.isVirtual && venue.id) ?? false

export const shouldDisplayEACInformationSectionForVenue = (
  venue?: GetOffererVenueResponseModel | GetVenueResponseModel
): boolean => {
  const dmsInformations = getLastCollectiveDmsApplication(
    venue?.collectiveDmsApplications ?? []
  )

  return (
    Boolean(dmsInformations) &&
    (dmsInformations?.state === DMSApplicationstatus.EN_INSTRUCTION ||
      dmsInformations?.state === DMSApplicationstatus.EN_CONSTRUCTION)
  )
}

export const shouldShowVenueOfferStepsForVenue = (
  venue?: GetOffererVenueResponseModel | GetVenueResponseModel
) =>
  shouldDisplayEACInformationSectionForVenue(venue) ||
  (venue && !('hasCreatedOffer' in venue)
    ? !venue.hasOffers
    : !venue?.hasCreatedOffer)
