/* istanbul ignore file */
import { api } from 'apiClient/api'

export const loadFakeApiVenueStats = venue =>
  vi.spyOn(api, 'getVenueStats').mockResolvedValue(venue)

export const generateFakeOffererApiKey = apiKey =>
  vi.spyOn(api, 'generateApiKeyRoute').mockResolvedValue({ apiKey })

export const failToGenerateOffererApiKey = () =>
  vi.spyOn(api, 'generateApiKeyRoute').mockRejectedValue(null)
