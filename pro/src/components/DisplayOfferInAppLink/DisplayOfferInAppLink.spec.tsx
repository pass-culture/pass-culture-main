import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { WEBAPP_URL } from '@/commons/utils/config'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { DisplayOfferInAppLink } from './DisplayOfferInAppLink'

const mockLogEvent = vi.fn()
const mockFocus = vi.fn()

describe('DisplayOfferInAppLink', () => {
  beforeEach(() => {
    vi.spyOn(window, 'open').mockReturnValue({
      focus: mockFocus,
    } as unknown as Window)

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should render a link with correct URL and children', () => {
    const offerId = 123

    renderWithProviders(
      <DisplayOfferInAppLink id={offerId} label="View in app" />
    )

    const link = screen.getByRole('link', {
      name: 'Nouvelle fenêtreView in app',
    })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', `${WEBAPP_URL}/offre/${offerId}`)
  })

  it('should log event when clicked', async () => {
    const offerId = 456

    renderWithProviders(
      <DisplayOfferInAppLink id={offerId} label="View in app" />
    )

    const link = screen.getByRole('link', {
      name: 'Nouvelle fenêtreView in app',
    })
    await userEvent.click(link)

    expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_VIEW_APP_OFFER, {
      offerId,
    })
  })
})
