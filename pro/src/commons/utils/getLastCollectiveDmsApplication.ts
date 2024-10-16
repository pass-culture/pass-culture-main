import {
  DMSApplicationForEAC,
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'

export const getLastCollectiveDmsApplication = (
  collectiveDmsApplications: DMSApplicationForEAC[]
): DMSApplicationForEAC | null => {
  if (collectiveDmsApplications.length === 0) {
    return null
  }

  return collectiveDmsApplications.reduce((previous, current) =>
    new Date(previous.lastChangeDate) > new Date(current.lastChangeDate)
      ? previous
      : current
  )
}

export const getLastDmsApplicationForOfferer = (
  venueId?: string | null,
  offerer?: GetOffererResponseModel
) => {
  if (!offerer) {
    return
  }
  if (venueId) {
    const venue = offerer.managedVenues?.find(
      (venue) => venue.id.toString() === venueId
    )
    if (venue) {
      return getLastCollectiveDmsApplication(venue.collectiveDmsApplications)
    }
  }
  return offerer.managedVenues?.reduce(
    (
      mostRecent: DMSApplicationForEAC | null,
      venue: GetOffererVenueResponseModel
    ) => {
      const lastDmsApplication = getLastCollectiveDmsApplication(
        venue.collectiveDmsApplications
      )
      return !mostRecent ||
        (lastDmsApplication &&
          lastDmsApplication.lastChangeDate > mostRecent.lastChangeDate)
        ? lastDmsApplication
        : mostRecent
    },
    null
  )
}
