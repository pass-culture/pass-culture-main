import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import * as useAnalytics from 'hooks/useAnalytics'
import { collectiveBookingRecapFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { BookingOfferCell, BookingOfferCellProps } from '../BookingOfferCell'

const mockLogEvent = vi.fn()

const renderOfferCell = (props: BookingOfferCellProps) => {
  renderWithProviders(<BookingOfferCell {...props} />)
}

describe('BookingOfferCell', () => {
  it('should call tracker with params', async () => {
    // Given
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    const props: BookingOfferCellProps = {
      booking: collectiveBookingRecapFactory({
        stock: {
          offerId: 1,
          offerName: 'Guitare acoustique',
          offerIsEducational: false,
          eventBeginningDatetime: new Date().toISOString(),
          numberOfTickets: 1,
        },
      }),
    }

    // When
    renderOfferCell(props)
    await userEvent.click(screen.getByText('Guitare acoustique'))
  })
})
