import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { collectiveBookingRecapFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import BookingOfferCell, { BookingOfferCellProps } from '../BookingOfferCell'

const mockLogEvent = vi.fn()

const renderOfferCell = (props: BookingOfferCellProps) => {
  renderWithProviders(<BookingOfferCell {...props} />)
}

describe('BookingOfferCell', () => {
  it('should call tracker with params', async () => {
    // Given
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    const props = {
      offer: {
        offerId: 1,
        offerIdentifier: 'A1',
        offerName: 'Guitare acoustique',
        type: 'thing',
        venueDepartmentCode: '93',
        offerIsEducational: false,
        eventBeginningDatetime: new Date().toISOString(),
        numberOfTickets: 1,
      },
      bookingRecapInfo: {
        original: collectiveBookingRecapFactory(),
      } as Row<CollectiveBookingResponseModel>,
      isCollective: false,
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
