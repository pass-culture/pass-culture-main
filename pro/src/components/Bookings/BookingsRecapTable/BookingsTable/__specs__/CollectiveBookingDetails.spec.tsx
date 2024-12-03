import { screen, waitFor } from '@testing-library/react'

import { api } from 'apiClient/api'
import { CollectiveOfferAllowedAction } from 'apiClient/v1'
import {
  collectiveBookingByIdFactory,
  collectiveBookingFactory,
  getCollectiveOfferFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { CollectiveBookingDetails } from '../CollectiveBookingDetails'

describe('CollectiveBookingDetails', () => {
  it('should render contact details and buttons correctly', () => {
    const bookingRecap = collectiveBookingFactory()
    const bookingDetails = collectiveBookingByIdFactory()

    renderWithProviders(
      <CollectiveBookingDetails
        bookingDetails={bookingDetails}
        bookingRecap={bookingRecap}
      />
    )

    expect(
      screen.getByText(/Contact de l’établissement scolaire/)
    ).toBeInTheDocument()
    expect(screen.getByText(/LYCEE De Paris/)).toBeInTheDocument()
    expect(screen.getByText(/0601020304/)).toBeInTheDocument()
    expect(screen.getByText(/Jean Dupont/)).toBeInTheDocument()
    expect(screen.getByText(/test@example.com/)).toBeInTheDocument()
  })

  it('should show cancel button when ENABLE_COLLECTIVE_NEW_STATUSES is on and offer has CAN_CANCEL allowed action', async () => {
    const offer = getCollectiveOfferFactory({
      allowedActions: [CollectiveOfferAllowedAction.CAN_CANCEL],
      id: 1,
    })

    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(offer)

    const bookingRecap = collectiveBookingFactory()
    const bookingDetails = collectiveBookingByIdFactory()

    renderWithProviders(
      <CollectiveBookingDetails
        bookingDetails={bookingDetails}
        bookingRecap={bookingRecap}
      />,
      {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    )

    expect(
      await screen.findByText('Annuler la préréservation')
    ).toBeInTheDocument()
  })

  it('should not show cancel button when ENABLE_COLLECTIVE_NEW_STATUSES is and offer has not CAN_CANCEL allowed action', async () => {
    const offer = getCollectiveOfferFactory({
      allowedActions: [],
      id: 1,
    })

    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(offer)

    const bookingRecap = collectiveBookingFactory()
    const bookingDetails = collectiveBookingByIdFactory()

    renderWithProviders(
      <CollectiveBookingDetails
        bookingDetails={bookingDetails}
        bookingRecap={bookingRecap}
      />,
      {
        features: ['ENABLE_COLLECTIVE_NEW_STATUSES'],
      }
    )

    await waitFor(() => {
      expect(
        screen.queryByText('Annuler la préréservation')
      ).not.toBeInTheDocument()
    })
  })
})
