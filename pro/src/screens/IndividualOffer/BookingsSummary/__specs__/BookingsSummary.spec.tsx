import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { IndividualOfferContext } from 'context/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  bookingRecapFactory,
} from 'utils/apiFactories'
import { individualOfferContextValuesFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { BookingsSummaryScreen } from '../BookingsSummary'

const render = (offer: GetIndividualOfferResponseModel) => {
  const contextValue = individualOfferContextValuesFactory({ offer })

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <BookingsSummaryScreen offer={offer} />
    </IndividualOfferContext.Provider>
  )
}

describe('BookingsSummary', () => {
  it('should render a list of bookings', async () => {
    const offer = getIndividualOfferFactory({ name: 'Offre de test' })

    vi.spyOn(api, 'getBookingsPro').mockResolvedValue({
      bookingsRecap: [
        bookingRecapFactory({}, offer),
        bookingRecapFactory({}, offer),
        bookingRecapFactory({}, offer),
      ],
      page: 1,
      pages: 1,
      total: 3,
    })

    render(offer)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(/Réservations/)).toBeInTheDocument()
    expect(screen.getAllByRole('link', { name: 'Offre de test' })).toHaveLength(
      3
    )
  })

  it('should render a message when no bookings', async () => {
    const offer = getIndividualOfferFactory({ name: 'Offre de test' })

    vi.spyOn(api, 'getBookingsPro').mockResolvedValue({
      bookingsRecap: [],
      page: 1,
      pages: 1,
      total: 0,
    })

    render(offer)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByText('Vous n’avez pas encore de réservations')
    ).toBeInTheDocument()
  })
})
