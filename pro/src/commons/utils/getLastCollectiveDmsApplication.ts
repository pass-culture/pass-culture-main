import type {
  DMSApplicationForEAC,
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from '@/apiClient/v1'

export const getLastDmsApplicationForOfferer = (
  venueId?: string | null,
  offerer?: GetOffererResponseModel | null
) => {
  if (!offerer) {
    return
  }
  if (venueId) {
    const venue = offerer.managedVenues?.find(
      (venue) => venue.id.toString() === venueId
    )
    if (venue) {
      return venue.lastCollectiveDmsApplication
    }
  }
  return offerer.managedVenues?.reduce(
    (
      mostRecent: DMSApplicationForEAC | null,
      venue: GetOffererVenueResponseModel
    ) => {
      const lastDmsApplication = venue.lastCollectiveDmsApplication
      return !mostRecent ||
        (lastDmsApplication &&
          lastDmsApplication.lastChangeDate > mostRecent.lastChangeDate)
        ? lastDmsApplication
        : mostRecent
    },
    null
  )
}
