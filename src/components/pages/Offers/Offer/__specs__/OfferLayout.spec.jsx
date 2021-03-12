import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import OfferLayout from '../OfferLayout'

jest.mock('repository/pcapi/pcapi', () => ({
  loadOffer: jest.fn(),
}))

const renderOfferDetails = async (props, store) => {
  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter>
          <OfferLayout {...props} />
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('offerLayout', () => {
  let editedOffer
  let props
  let store

  beforeEach(() => {
    store = configureTestStore({ data: { users: [{ publicName: 'François', isAdmin: false }] } })
    props = {}
  })

  describe('render when editing an existing offer', () => {
    beforeEach(() => {
      editedOffer = {
        id: 'AB',
        name: 'My edited offer',
        status: 'SOLD_OUT'
      }
      props = {
        match: {
          url: '/offres/AB',
          params: { offerId: 'AB' },
        },
        location: {
          pathname: '/offres/AB/edition',
        },
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
    })

    it('should have title "Éditer une offre"', async () => {
      // When
      await renderOfferDetails(props, store)

      // Then
      const title = await screen.findByText('Éditer une offre', { selector: 'h1' })
      expect(title).toBeInTheDocument()
    })

    it('should display offer status', async () => {
      // when
      await renderOfferDetails(props, store)

      // then
      expect(await screen.getByText('épuisée')).toBeInTheDocument()
    })
  })

  describe('render when creating a new offer', () => {
    beforeEach(() => {
      props = {
        match: {
          url: '/offres',
          params: {},
        },
        location: {
          pathname: '/offres/AB/creation',
        },
      }
    })

    it('should have title "Ajouter une offre"', async () => {
      // When
      await renderOfferDetails(props, store)

      // Then
      expect(screen.getByText('Nouvelle offre', { selector: 'h1' })).toBeInTheDocument()
    })
  })

  describe('render when editing stocks', () => {
    beforeEach(() => {
      editedOffer = {
        id: 'AB',
        venue: {
          departementCode: '973',
        },
        isEvent: false,
        stocks: [],
      }
      props = {
        match: {
          url: '/offres/AB',
          params: { offerId: 'AB' },
        },
        location: {
          pathname: '/offres/AB/stocks',
        },
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
    })

    it('should have active tab "Stock et prix"', async () => {
      await renderOfferDetails(props, store)
      const stockTabLink = await screen.findByText('Stock et prix', { selector: 'a' })
      expect(stockTabLink.closest('.bc-step')).toHaveClass('active')
    })
  })
})
