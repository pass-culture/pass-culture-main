import '@testing-library/jest-dom'
import { act, render, screen, within } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'

import Venue from '../Venue'

const mockHistoryPush = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useHistory: () => ({
    push: mockHistoryPush,
  }),
}))

jest.mock('repository/pcapi/pcapi', () => ({
  getVenueStats: jest.fn(),
}))

let venueDefaultProps
const renderVenue = async props =>
  await act(async () => {
    await render(
      <MemoryRouter>
        <Venue
          {...venueDefaultProps}
          {...props}
        />
      </MemoryRouter>
    )
  })

describe('venues', () => {
  beforeEach(() => {
    venueDefaultProps = {
      id: 'venue_id',
      isVirtual: false,
      name: 'My venue',
      offererId: 'offerer_id',
      publicNam: 'My venue public name',
    }
  })
  describe('render', () => {
    it('should display stats tiles', async () => {
      // Given
      pcapi.getVenueStats.mockResolvedValue({
        activeBookingsQuantity: 0,
        usedBookingsQuantity: 1,
      })

      // When
      await renderVenue()

      // Then
      expect(pcapi.getVenueStats).toHaveBeenCalledWith(venueDefaultProps.id)

      const [
        activeOffersStat,
        activeBookingsStat,
        validatedBookingsStat,
        outOfStockOffersStat,
      ] = screen.getAllByTestId('venue-stat')
      expect(within(activeOffersStat).getByText('- -')).toBeInTheDocument()
      expect(within(activeOffersStat).getByText('Offres actives')).toBeInTheDocument()

      expect(within(activeBookingsStat).getByText('0')).toBeInTheDocument()
      expect(within(activeBookingsStat).getByText('Réservations en cours')).toBeInTheDocument()

      expect(within(validatedBookingsStat).getByText('1')).toBeInTheDocument()
      expect(within(validatedBookingsStat).getByText('Réservations validées')).toBeInTheDocument()

      expect(within(outOfStockOffersStat).getByText('- -')).toBeInTheDocument()
      expect(within(outOfStockOffersStat).getByText('Offres stocks épuisés')).toBeInTheDocument()
    })

    it('should contain a link for each stats', async () => {
      // When
      await renderVenue()

      // Then
      expect(screen.getAllByText('Voir')).toHaveLength(4)
    })

    describe('render virtual venue', () => {
      beforeEach(async () => {
        await renderVenue({ isVirtual: true })
      })

      it('should display create offer link', () => {
        expect(screen.getByText('Créer une nouvelle offre numérique')).toBeInTheDocument()
      })
    })

    describe('render physical venue', () => {
      beforeEach(async () => {
        await renderVenue({ isVirtual: false })
      })

      it('should display create offer link', () => {
        expect(screen.getByText('Créer une nouvelle offre')).toBeInTheDocument()
      })
    })
  })
})
