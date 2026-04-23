import {
  DMSApplicationstatus,
  type GetVenueResponseModel,
} from '@/apiClient/v1'

export const shouldDisplayEACInformationSectionForVenue = (
  venue: GetVenueResponseModel
): boolean =>
  venue.lastCollectiveDmsApplication?.state ===
    DMSApplicationstatus.EN_INSTRUCTION ||
  venue.lastCollectiveDmsApplication?.state ===
    DMSApplicationstatus.EN_CONSTRUCTION
