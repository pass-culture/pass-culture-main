import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'
import '@testing-library/jest-dom'

import { OfferAddressType, StudentLevels } from 'apiClient/v1'
import { configureTestStore } from 'store/testUtils'

import CollectiveBookingDetails from '../CollectiveBookingDetails'

jest.mock('apiClient/api', () => ({
  api: {
    cancelCollectiveOfferBooking: jest.fn().mockResolvedValue({}),
  },
}))

const bookingDetails = {
  id: 1,
  beginningDatetime: new Date('2022-01-23T10:30:00').toISOString(),
  venuePostalCode: '75017',
  offerVenue: {
    addressType: OfferAddressType.OFFERER_VENUE,
    otherAddress: '',
    venueId: 'V1',
  },
  numberOfTickets: 10,
  price: 0,
  students: [StudentLevels.COLL_GE_4E],
  educationalInstitution: {
    institutionType: 'LYCEE PROFESIONNEL',
    name: 'Métier Alexandre Bérard',
    postalCode: '01500',
    city: 'Ambérieu-en-Buguey',
    id: 1,
    phoneNumber: '0672930477',
  },
  educationalRedactor: {
    firstName: 'Benoit',
    lastName: 'Demon',
    email: 'benoit.demon@lyc-alexandreberard.com',
    civility: 'M',
    id: 1,
  },
  isCancellable: true,
}

describe('CollectiveBookingDetails', () => {
  it('should reload bookings after cancelling one', async () => {
    const reloadBookings = jest.fn()

    render(
      <Provider store={configureTestStore({})}>
        <Router history={createBrowserHistory()}>
          <CollectiveBookingDetails
            bookingDetails={bookingDetails}
            reloadBookings={reloadBookings}
            offerId="A1"
            canCanelBooking={true}
          />
        </Router>
      </Provider>
    )

    await userEvent.click(
      await screen.findByRole('button', { name: 'Annuler la réservation' })
    )
    await waitFor(() => expect(reloadBookings).toHaveBeenCalledTimes(1))
  })

  it('Cancel booking button should be disabled when booking cannot be cancelled', async () => {
    render(
      <Provider store={configureTestStore({})}>
        <Router history={createBrowserHistory()}>
          <CollectiveBookingDetails
            bookingDetails={bookingDetails}
            reloadBookings={jest.fn()}
            offerId="A1"
            canCanelBooking={false}
          />
        </Router>
      </Provider>
    )

    expect(
      await screen.findByRole('button', { name: 'Annuler la réservation' })
    ).toBeDisabled()
  })
})
