import { api } from 'apiClient/api'
import { waitFor } from '@testing-library/react'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { useLoadFeatureFlags } from '../useLoadFeatureFlags'

const FeatureFlagsLoader = (): null => {
  useLoadFeatureFlags()
  return null
}

const renderFeaturesFlagsLoader = (lastLoaded?: number) => {
  const storeOverrides = {
    features: {
      list: [],
      lastLoaded,
    },
  }

  renderWithProviders(<FeatureFlagsLoader />, { storeOverrides })
}

describe('useLoadFeatureFlags', () => {
  it('should load features when lastLoaded is not defined', async () => {
    vi.spyOn(api, 'listFeatures').mockResolvedValue([])
    renderFeaturesFlagsLoader()

    await waitFor(() => {
      expect(api.listFeatures).toHaveBeenCalled()
    })
  })

  it('should load features after 30 min', async () => {
    vi.spyOn(api, 'listFeatures').mockResolvedValue([])

    renderFeaturesFlagsLoader(Date.now() - 1000 * 60 * 31)
    await waitFor(() => {
      expect(api.listFeatures).toHaveBeenCalledTimes(1)
    })
  })

  it('should not load features before 30 min', async () => {
    vi.spyOn(api, 'listFeatures').mockResolvedValue([])

    renderFeaturesFlagsLoader(Date.now() - 1000 * 60 * 20)

    await waitFor(() => {
      expect(api.listFeatures).not.toHaveBeenCalled()
    })
  })
})
