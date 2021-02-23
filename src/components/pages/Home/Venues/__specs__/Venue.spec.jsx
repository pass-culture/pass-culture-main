import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import Venue from '../Venue'

const mockHistoryPush = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useHistory: () => ({
    push: mockHistoryPush,
  }),
}))

const renderVenue = async props => {
  const venueDefaultProps = {
    id: 'venue_id',
    isVirtual: false,
    name: 'My venue',
    offererId: 'offerer_id',
    publicNam: 'My venue public name',
  }

  return await act(async () => {
    await render(
      <MemoryRouter>
        <Venue
          {...venueDefaultProps}
          {...props}
        />
      </MemoryRouter>
    )
  })
}

describe('venues', () => {
  describe('render', () => {
    describe('render virtual venue', () => {
      beforeEach(async () => {
        await renderVenue({ isVirtual: true })
      })

      it('should display create offer link', () => {
        expect(screen.getByText('Créer une nouvelle offre numérique')).toBeInTheDocument()
      })

      it('should display stats titles', () => {
        expect(screen.getByText('Offres actives')).toBeInTheDocument()
        expect(screen.getByText('Reservations en cours')).toBeInTheDocument()
        expect(screen.getByText('Reservations en validées')).toBeInTheDocument()
        expect(screen.getByText('Offres stocks épuisés')).toBeInTheDocument()
      })

      it('should contain a link for each stats', () => {
        expect(screen.getAllByText('Voir')).toHaveLength(4)
      })
    })

    describe('render physical nenue', () => {
      beforeEach(async () => {
        await renderVenue({ isVirtual: false })
      })

      it('should display create offer link', () => {
        expect(screen.getByText('Créer une nouvelle offre')).toBeInTheDocument()
      })
    })
  })
})
