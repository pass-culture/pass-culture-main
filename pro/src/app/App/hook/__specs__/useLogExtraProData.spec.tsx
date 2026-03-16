import { screen, waitFor } from '@testing-library/react'
import { beforeEach } from 'vitest'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { useLogExtraProData } from '@/app/App/hook/useLogExtraProData'
import { HeaderDropdown } from '@/app/App/layouts/components/Header/components/HeaderDropdown/HeaderDropdown'
import type { DeepPartial } from '@/commons/custom_types/utils'
import type { RootState } from '@/commons/store/store'
import { getOffererNameFactory } from '@/commons/utils/factories/individualApiFactories'
import { currentOffererFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

const mockLogEvent = vi.fn()

const Logger = (): null => {
  useLogExtraProData()
  return null
}

const renderLogExtraProData = async (
  features: string[] = [],
  overrides: DeepPartial<RootState> = {}
) => {
  const rendered = renderWithProviders(
    <>
      <Logger />
      <HeaderDropdown />
    </>,
    {
      initialRouterEntries: ['/accueil'],
      features,
      storeOverrides: {
        ...overrides,
        offerer: currentOffererFactory({
          offererNamesAttached: [
            getOffererNameFactory({ id: 1 }),
            getOffererNameFactory({ id: 2, name: 'super structure' }),
          ],
        }),
      },
    }
  )

  await waitFor(() => {
    expect(screen.queryByTestId('profile-button')).toBeInTheDocument()
  })

  return rendered
}

describe('useLogExtraProData', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should log an event on page load', async () => {
    await renderLogExtraProData()

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, 'extra_pro_data', {
      offerer_id: 1,
      from: '/accueil',
    })
  })

  it('should log an event on page load with FF WIP_SWITCH_VENUE', async () => {
    await renderLogExtraProData(['WIP_SWITCH_VENUE'])

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, 'extra_pro_data', {
      offerer_id: 1,
      from: '/accueil',
    })
  })

  it('should log an event on page load with FF WIP_SWITCH_VENUE and a venue', async () => {
    await renderLogExtraProData(['WIP_SWITCH_VENUE'], {
      user: {
        selectedVenue: { id: 123, publicName: 'toto' },
      },
    })

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, 'extra_pro_data', {
      offerer_id: 1,
      venue_id: 123,
      from: '/accueil',
    })
  })
})
