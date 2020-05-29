import { fetchFromApiWithCredentials } from '../utils/fetch'

export const fetchAllVenuesByProUser = () => {
  return fetchFromApiWithCredentials('/venues')
    .catch(() => [])
}
