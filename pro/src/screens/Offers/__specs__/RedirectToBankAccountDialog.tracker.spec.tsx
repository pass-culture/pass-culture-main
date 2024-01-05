import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import * as useAnalytics from 'hooks/useAnalytics'
import {
  RedirectToBankAccountDialog,
  RedirectToBankAccountDialogProps,
} from 'screens/Offers/RedirectToBankAccountDialog'
import { renderWithProviders } from 'utils/renderWithProviders'

const mockLogEvent = vi.fn()
const renderDialog = (props: RedirectToBankAccountDialogProps) => {
  renderWithProviders(<RedirectToBankAccountDialog {...props} />)
}

describe('screen Offers', () => {
  let props: RedirectToBankAccountDialogProps
  beforeEach(() => {
    props = {
      cancelRedirectUrl: '/url',
      offerId: 1,
      venueId: 2,
    }

    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should track event on cancel', async () => {
    renderDialog(props)

    await userEvent.click(screen.getByText('Plus tard'))

    expect(mockLogEvent).toHaveBeenCalledWith(
      'hasClickedSeeLaterFromSuccessOfferCreationModal',
      {
        from: 'recapitulatif',
      }
    )
  })
  it('should track event on redirect', async () => {
    renderDialog(props)

    await userEvent.click(
      screen.getByText('Renseigner des coordonnées bancaires')
    )

    expect(mockLogEvent).toHaveBeenCalledWith('hasClickedVenueAddRibButton', {
      from: 'recapitulatif',
      venue_id: 2,
    })
  })
})
