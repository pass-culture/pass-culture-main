/* istanbul ignore file */
import { api } from 'apiClient/api'

export const loadFakeApiVenueStats = venue =>
  jest.spyOn(api, 'getVenueStats').mockResolvedValue(venue)

export const generateFakeOffererApiKey = apiKey =>
  jest.spyOn(api, 'generateApiKeyRoute').mockResolvedValue({ apiKey })

export const failToGenerateOffererApiKey = () =>
  jest.spyOn(api, 'generateApiKeyRoute').mockRejectedValue(null)
