import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as useAnalytics from 'app/App/analytics/firebase'
import { HeadlineOfferContextProvider } from 'commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { venueListItemFactory } from 'commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { api } from 'apiClient/api'
import { HeadlineOffer } from './HeadlineOffer'

describe('HeadlineOffer', () => {
  it('should log when cultural actor click on see in app', async () => {
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(api, 'getOffererHeadlineOffer').mockResolvedValue({
      id: 42,
      name: 'My offer',
      venueId: 1,
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        venueListItemFactory({
          id: 1,
          name: 'Une venue physique & permanente',
        }),
      ],
    })
    const user = sharedCurrentUserFactory()
    renderWithProviders(
      <HeadlineOfferContextProvider>
        <HeadlineOffer />
      </HeadlineOfferContextProvider>,
      {
        user,
        storeOverrides: {
          user: {
            currentUser: user,
          },
          offerer: currentOffererFactory(),
        },
      }
    )

    await userEvent.click(
      await screen.findByText('Visualiser dans l’application')
    )

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      'hasClickedViewAppHeadlineOffer',
      {
        offerId: 42,
        userId: 1,
      }
    )
  })
})
