import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import {
  CollectiveBookingBankInformationStatus,
  OfferAddressType,
  StudentLevels,
} from 'apiClient/v1'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveBookingDetails from '../CollectiveBookingDetails'

jest.mock('apiClient/api', () => ({
  api: {
    cancelCollectiveOfferBooking: jest.fn().mockResolvedValue({}),
  },
}))

const bookingDetails = {
  id: 1,
  bankInformationStatus: CollectiveBookingBankInformationStatus.ACCEPTED,
  beginningDatetime: new Date('2022-01-23T10:30:00').toISOString(),
  venuePostalCode: '75017',
  offerVenue: {
    addressType: OfferAddressType.OFFERER_VENUE,
    otherAddress: '',
    venueId: 'V1',
  },
  venueId: 'A1',
  offererId: 'O1',
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
    institutionId: 'ABCDEF11',
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

    renderWithProviders(
      <CollectiveBookingDetails
        bookingDetails={bookingDetails}
        reloadBookings={reloadBookings}
        offerId="A1"
        canCancelBooking={true}
      />
    )

    await userEvent.click(
      await screen.findByRole('button', { name: 'Annuler la réservation' })
    )
    expect(
      screen.queryByText('Voulez-vous annuler la réservation ?')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Confirmer' }))
    expect(api.cancelCollectiveOfferBooking).toHaveBeenCalledWith('A1')
    await waitFor(() => expect(reloadBookings).toHaveBeenCalledTimes(1))
  })

  it('Cancel booking button should be disabled when booking cannot be cancelled', async () => {
    renderWithProviders(
      <CollectiveBookingDetails
        bookingDetails={bookingDetails}
        reloadBookings={jest.fn()}
        offerId="A1"
        canCancelBooking={false}
      />
    )

    expect(
      await screen.findByRole('button', { name: 'Annuler la réservation' })
    ).toBeDisabled()
  })
})
