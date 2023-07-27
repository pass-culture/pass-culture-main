import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import BookingOfferCell from '../BookingOfferCell'

const mockLogEvent = vi.fn()

const renderOfferCell = props => {
  const storeOverrides = { app: { logEvent: mockLogEvent } }

  renderWithProviders(<BookingOfferCell {...props} />, { storeOverrides })
}

describe('tracking bookings offer cell', () => {
  it('should call tracker with params', async () => {
    // Given
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    const props = {
      offer: {
        offerIdentifier: 'A1',
        offerName: 'Guitare acoustique',
        type: 'thing',
        venueDepartmentCode: '93',
        offerIsEducational: false,
      },
    }

    // When
    renderOfferCell(props)
    await userEvent.click(screen.getByText('Guitare acoustique'))

    // Then
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'Bookings',
        isEdition: true,
        to: 'recapitulatif',
        used: 'BookingsTitle',
      }
    )
  })
})
