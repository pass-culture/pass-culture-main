import { waitFor } from '@testing-library/react'

import { apiNew } from '@/apiClient/api'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

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
    vi.spyOn(apiNew, 'listFeatures').mockResolvedValue([])
    renderFeaturesFlagsLoader()

    await waitFor(() => {
      expect(apiNew.listFeatures).toHaveBeenCalled()
    })
  })

  it('should load empty features when no data is returned', async () => {
    vi.spyOn(apiNew, 'listFeatures').mockResolvedValue(undefined)
    renderFeaturesFlagsLoader()

    await waitFor(() => {
      expect(apiNew.listFeatures).toHaveBeenCalled()
    })
  })

  it('should load features after 30 min', async () => {
    vi.spyOn(apiNew, 'listFeatures').mockResolvedValue([])

    renderFeaturesFlagsLoader(Date.now() - 1000 * 60 * 31)
    await waitFor(() => {
      expect(apiNew.listFeatures).toHaveBeenCalledTimes(1)
    })
  })

  it('should not load features before 30 min', async () => {
    vi.spyOn(apiNew, 'listFeatures').mockResolvedValue([])

    renderFeaturesFlagsLoader(Date.now() - 1000 * 60 * 20)

    await waitFor(() => {
      expect(apiNew.listFeatures).not.toHaveBeenCalled()
    })
  })
})
