import '@testing-library/jest-dom'

import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import type { Store } from 'redux'

import { api } from 'apiClient/api'
import * as useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import { configureTestStore } from 'store/testUtils'
import { loadFakeApiVenueStats } from 'utils/fakeApi'

import Venue, { IVenueProps } from '../Venue'

jest.mock('apiClient/api', () => ({
  api: {
    getVenueStats: jest.fn().mockResolvedValue({}),
  },
}))

const renderVenue = (props: IVenueProps, store: Store) => {
  render(
    <Provider store={store}>
      <MemoryRouter>
        <Venue {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('venues', () => {
  let props: IVenueProps
  let store: Store

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
    renderVenue(props, store)

    await userEvent.click(
      screen.getByTitle('Afficher les statistiques de My venue')
    )

    // Then
    expect(api.getVenueStats).toHaveBeenCalledWith(props.id)

    const [
      activeOffersStat,
      activeBookingsStat,
      validatedBookingsStat,
      outOfStockOffersStat,
    ] = screen.getAllByTestId('venue-stat')

    expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

    expect(
      within(activeOffersStat).getByText('Offres publiées')
    ).toBeInTheDocument()

    expect(within(activeBookingsStat).getByText('0')).toBeInTheDocument()
    expect(
      within(activeBookingsStat).getByText('Réservations en cours')
    ).toBeInTheDocument()

    expect(within(validatedBookingsStat).getByText('1')).toBeInTheDocument()
    expect(
      within(validatedBookingsStat).getByText('Réservations validées')
    ).toBeInTheDocument()

    expect(within(outOfStockOffersStat).getByText('3')).toBeInTheDocument()
    expect(
      within(outOfStockOffersStat).getByText('Offres stocks épuisés')
    ).toBeInTheDocument()
  })

  it('should contain a link for each stats', async () => {
    // When
    renderVenue(props, store)
    await userEvent.click(
      screen.getByTitle('Afficher les statistiques de My venue')
    )
    const [activeOffersStat] = screen.getAllByTestId('venue-stat')
    expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

    // Then
    expect(screen.getAllByRole('link', { name: 'Voir' })).toHaveLength(4)
  })

  it('should redirect to filtered bookings when clicking on link', async () => {
    // When
    renderVenue(props, store)
    await userEvent.click(
      screen.getByTitle('Afficher les statistiques de My venue')
    )
    // Then
    const [
      activeOffersStat,
      activeBookingsStat,
      validatedBookingsStat,
      outOfStockOffersStat,
    ] = screen.getAllByTestId('venue-stat')

    expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

    expect(
      within(activeOffersStat).getByRole('link', { name: 'Voir' })
    ).toHaveAttribute('href', '/offres?lieu=VENUE01&statut=active')
    const byRole = within(validatedBookingsStat).getByRole('link', {
      name: 'Voir',
    })
    expect(byRole).toHaveAttribute(
      'href',
      '/reservations?page=1&bookingStatusFilter=validated&offerVenueId=VENUE01'
    )
    expect(
      within(activeBookingsStat).getByRole('link', { name: 'Voir' })
    ).toHaveAttribute('href', '/reservations?page=1&offerVenueId=VENUE01')
    expect(
      within(outOfStockOffersStat).getByRole('link', { name: 'Voir' })
    ).toHaveAttribute('href', '/offres?lieu=VENUE01&statut=epuisee')
  })

  describe('virtual venue section', () => {
    it('should display create offer link', async () => {
      // Given
      props.isVirtual = true

      // When
      renderVenue(props, store)
      await userEvent.click(
        screen.getByTitle('Afficher les statistiques de My venue')
      )
      const [activeOffersStat] = screen.getAllByTestId('venue-stat')
      expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

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
      renderVenue(props, store)
      await userEvent.click(
        screen.getByTitle('Afficher les statistiques de My venue')
      )
      const [activeOffersStat] = screen.getAllByTestId('venue-stat')
      expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

      // Then
      expect(
        screen.getByRole('link', { name: 'Créer une nouvelle offre' })
      ).toBeInTheDocument()
    })

    it('should display edition venue link', async () => {
      // Given
      props.isVirtual = false

      // When
      renderVenue(props, store)
      await userEvent.click(
        screen.getByTitle('Afficher les statistiques de My venue')
      )
      const [activeOffersStat] = screen.getAllByTestId('venue-stat')
      expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

      // Then
      expect(screen.getByRole('link', { name: 'Modifier' })).toHaveAttribute(
        'href',
        '/structures/OFFERER01/lieux/VENUE01?modification'
      )
    })

    it('should display edition venue link with new offer creation journey', async () => {
      // Given
      props.isVirtual = false
      await jest
        .spyOn(useNewOfferCreationJourney, 'default')
        .mockReturnValue(true)
      // When
      renderVenue(props, store)

      // Then
      expect(
        screen.getByRole('link', { name: 'Éditer le lieu' })
      ).toHaveAttribute(
        'href',
        '/structures/OFFERER01/lieux/VENUE01?modification'
      )
    })

    it('should display add bank information when venue does not have a reimbursement point', () => {
      // Given
      props.hasMissingReimbursementPoint = true

      // When
      renderVenue(props, store)

      // Then
      expect(
        screen.getByRole('link', { name: 'Ajouter un RIB' })
      ).toHaveAttribute(
        'href',
        '/structures/OFFERER01/lieux/VENUE01?modification#remboursement'
      )
    })
  })
})
