import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import * as useAnalytics from 'components/hooks/useAnalytics'
import { Events } from 'core/FirebaseEvents/constants'
import { configureTestStore } from 'store/testUtils'

import BookingOfferCell from '../BookingOfferCell'

const mockLogEvent = jest.fn()

const renderOfferCell = props => {
  const store = configureTestStore({ app: { logEvent: mockLogEvent } })

  render(
    <Provider store={store}>
      <BookingOfferCell {...props} />
    </Provider>
  )
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
        offer_identifier: 'A1',
        offer_name: 'Guitare acoustique',
        type: 'thing',
        venue_department_code: '93',
        offer_is_educational: false,
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
