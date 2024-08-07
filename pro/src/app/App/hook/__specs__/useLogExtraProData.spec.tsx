import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { beforeEach } from 'vitest'

import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import { useLogExtraProData } from 'app/App/hook/useLogExtraProData'
import { HeaderDropdown } from 'components/Header/HeaderDropdown/HeaderDropdown'
import { getOffererNameFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

const mockLogEvent = vi.fn()

const Logger = (): null => {
  useLogExtraProData()
  return null
}

const renderLogExtraProData = async () => {
  const rendered = renderWithProviders(
    <>
      <Logger />
      <HeaderDropdown />
    </>,
    {
      initialRouterEntries: ['/accueil'],
    }
  )

  await waitFor(() => {
    expect(api.listOfferersNames).toHaveBeenCalled()
  })

  await waitFor(() => {
    expect(screen.queryByTestId('offerer-select')).toBeInTheDocument()
  })

  return rendered
}

describe('useLogExtraProData', () => {
  beforeEach(() => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({ id: 1 }),
        getOffererNameFactory({ id: 2, name: 'super structure' }),
      ],
    })
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

  it('should log another event on offerer change', async () => {
    await renderLogExtraProData()

    await userEvent.click(screen.getByTestId('offerer-select'))
    await userEvent.click(screen.getByText(/Changer de structure/))
    await userEvent.click(screen.getByText('super structure'))

    expect(mockLogEvent).toHaveBeenCalledTimes(2)
    expect(mockLogEvent).toHaveBeenNthCalledWith(2, 'extra_pro_data', {
      offerer_id: 2,
      from: '/accueil',
    })
  })
})
