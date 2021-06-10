import '@testing-library/jest-dom'
import { act, render, screen, within } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import Venue from 'components/pages/Home/Venues/Venue'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { loadFakeApiVenueStats } from 'utils/fakeApi'

const renderVenue = async (props, store) => {
  return await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter>
          <Venue {...props} />
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('venues', () => {
  let props
  let store

  beforeEach(() => {
    store = configureTestStore()
    props = {
      id: 'VENUE01',
      isVirtual: false,
      name: 'My venue',
      offererId: 'OFFERER01',
    }
    loadFakeApiVenueStats({
      activeBookingsQuantity: 0,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 1,
    })
  })

  it('should display stats tiles', async () => {
    // When
    await renderVenue(props, store)

    // Then
    expect(pcapi.getVenueStats).toHaveBeenCalledWith(props.id)
    const [
      activeOffersStat,
      activeBookingsStat,
      validatedBookingsStat,
      outOfStockOffersStat,
    ] = screen.getAllByTestId('venue-stat')
    expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()
    expect(within(activeOffersStat).getByText('Offres actives')).toBeInTheDocument()

    expect(within(activeBookingsStat).getByText('0')).toBeInTheDocument()
    expect(within(activeBookingsStat).getByText('Réservations en cours')).toBeInTheDocument()

    expect(within(validatedBookingsStat).getByText('1')).toBeInTheDocument()
    expect(within(validatedBookingsStat).getByText('Réservations validées')).toBeInTheDocument()

    expect(within(outOfStockOffersStat).getByText('3')).toBeInTheDocument()
    expect(within(outOfStockOffersStat).getByText('Offres stocks épuisés')).toBeInTheDocument()
  })

  it('should contain a link for each stats', async () => {
    // When
    await renderVenue(props, store)

    // Then
    expect(screen.getAllByRole('link', { name: 'Voir' })).toHaveLength(4)
  })

  it('should redirect to filtered bookings when clicking on link', async () => {
    // When
    await renderVenue(props, store)

    // Then
    const [
      activeOffersStat,
      activeBookingsStat,
      validatedBookingsStat,
      outOfStockOffersStat,
    ] = screen.getAllByTestId('venue-stat')
    expect(within(activeOffersStat).getByRole('link', { name: 'Voir' })).toHaveAttribute(
      'href',
      '/offres?lieu=VENUE01&statut=active'
    )
    const byRole = within(validatedBookingsStat).getByRole('link', { name: 'Voir' })
    expect(byRole).toHaveAttribute('href', '/reservations')
    expect(within(activeBookingsStat).getByRole('link', { name: 'Voir' })).toHaveAttribute(
      'href',
      '/reservations'
    )
    expect(within(outOfStockOffersStat).getByRole('link', { name: 'Voir' })).toHaveAttribute(
      'href',
      '/offres?lieu=VENUE01&statut=epuisee'
    )
  })

  describe('virtual venue section', () => {
    it('should display create offer link', async () => {
      // Given
      props.isVirtual = true

      // When
      await renderVenue(props, store)

      // Then
      expect(
        screen.getByRole('link', { name: 'Créer une nouvelle offre numérique' })
      ).toBeInTheDocument()
    })
  })

  describe('physical venue section', () => {
    it('should display create offer link', async () => {
      // Given
      props.isVirtual = false

      // When
      await renderVenue(props, store)

      // Then
      expect(screen.getByRole('link', { name: 'Créer une nouvelle offre' })).toBeInTheDocument()
    })

    it('should display edition venue link', async () => {
      // Given
      props.isVirtual = false

      // When
      await renderVenue(props, store)

      // Then
      expect(screen.getByRole('link', { name: 'Modifier' }).href).toBe(
        'http://localhost/structures/OFFERER01/lieux/VENUE01?modification'
      )
    })
  })
})
