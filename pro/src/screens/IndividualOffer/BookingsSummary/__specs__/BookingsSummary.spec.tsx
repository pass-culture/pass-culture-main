import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { IndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import {
  bookingRecapFactory,
  getIndividualOfferFactory,
  bookingRecapStockFactory,
  individualOfferContextValuesFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { BookingsSummaryScreen } from '../BookingsSummary'

const render = (offer: GetIndividualOfferWithAddressResponseModel) => {
  const contextValue = individualOfferContextValuesFactory({ offer })

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <BookingsSummaryScreen offer={offer} />
    </IndividualOfferContext.Provider>
  )
}

describe('BookingsSummary', () => {
  beforeEach(() => {
    vi.spyOn(
      api,
      'getOfferPriceCategoriesAndSchedulesByDates'
    ).mockResolvedValue([])
  })
  it('should render a list of bookings', async () => {
    const offer = getIndividualOfferFactory({ name: 'Offre de test' })

    vi.spyOn(api, 'getBookingsPro').mockResolvedValueOnce({
      bookingsRecap: [
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: 'Offre de test' }),
        }),
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: 'Offre de test' }),
        }),
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: 'Offre de test' }),
        }),
      ],
      page: 1,
      pages: 1,
      total: 3,
    })

    render(offer)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(/Réservations/)).toBeInTheDocument()
    expect(
      await screen.findByRole('button', {
        name: 'Télécharger les réservations',
      })
    ).toBeInTheDocument()
    expect(screen.getAllByRole('link', { name: 'Offre de test' })).toHaveLength(
      3
    )
  })

  it('should render 1 bookings', async () => {
    const offer = getIndividualOfferFactory({ name: 'Offre de test' })

    vi.spyOn(api, 'getBookingsPro').mockResolvedValue({
      bookingsRecap: [
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: 'Offre de test' }),
        }),
      ],
      page: 1,
      pages: 1,
      total: 1,
    })

    render(offer)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(/Réservations/)).toBeInTheDocument()
    expect(
      await screen.findByRole('button', {
        name: 'Télécharger les réservations',
      })
    ).toBeInTheDocument()
    expect(screen.getAllByRole('link', { name: 'Offre de test' })).toHaveLength(
      1
    )
  })

  it('should render a message when no bookings', async () => {
    const offer = getIndividualOfferFactory({ name: 'Offre de test' })

    vi.spyOn(api, 'getBookingsPro').mockResolvedValueOnce({
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

  it('should open a download modal', async () => {
    const offer = getIndividualOfferFactory({ name: 'Offre de test' })

    vi.spyOn(api, 'getBookingsPro').mockResolvedValueOnce({
      bookingsRecap: [
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: 'Offre de test' }),
        }),
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: 'Offre de test' }),
        }),
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: 'Offre de test' }),
        }),
      ],
      page: 1,
      pages: 1,
      total: 3,
    })

    render(offer)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const downloadButton = await screen.findByRole('button', {
      name: 'Télécharger les réservations',
    })

    expect(downloadButton).toBeInTheDocument()

    await userEvent.click(downloadButton)

    expect(
      screen.getByText('Téléchargement de vos réservations')
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Télécharger au format CSV' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Télécharger au format Excel' })
    ).toBeInTheDocument()
  })
})
