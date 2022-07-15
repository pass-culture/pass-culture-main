import { GetVenueResponseModel } from 'apiClient/v1'

type VenueCollectiveInformation = Pick<
  GetVenueResponseModel,
  | 'collectiveDescription'
  | 'collectiveDomains'
  | 'collectiveEmail'
  | 'collectiveInterventionArea'
  | 'collectiveLegalStatus'
  | 'collectiveNetwork'
  | 'collectivePhone'
  | 'collectiveStudents'
  | 'collectiveWebsite'
>
export const venueHasCollectiveInformation = (
  venue: VenueCollectiveInformation
): boolean => {
  const collectiveKeys: (keyof VenueCollectiveInformation)[] = [
    'collectiveDescription',
    'collectiveDomains',
    'collectiveEmail',
    'collectiveInterventionArea',
    'collectiveLegalStatus',
    'collectiveNetwork',
    'collectivePhone',
    'collectiveStudents',
    'collectiveWebsite',
  ]

  return collectiveKeys.some(key => {
    const value = venue[key]
    return Array.isArray(value) ? value?.length > 0 : !!venue[key]
  })
}
