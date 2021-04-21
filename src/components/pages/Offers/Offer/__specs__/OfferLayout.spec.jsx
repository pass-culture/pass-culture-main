import { fireEvent } from '@testing-library/dom'
import '@testing-library/jest-dom'
import { act, render, screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import OfferLayout from '../OfferLayout'

jest.mock('repository/pcapi/pcapi', () => ({
  loadOffer: jest.fn(),
  updateOffersActiveStatus: jest.fn(),
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
        status: 'SOLD_OUT',
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

    it('should allow to activate inactive offer', async () => {
      // Given
      pcapi.updateOffersActiveStatus.mockReturnValue(Promise.resolve())
      pcapi.loadOffer
        .mockResolvedValueOnce({ ...editedOffer, isActive: false })
        .mockResolvedValue({ ...editedOffer, isActive: true })
      await renderOfferDetails(props, store)

      // When
      fireEvent.click(screen.getByRole('button', { name: "Activer l'offre" }))

      // Then
      expect(pcapi.updateOffersActiveStatus).toHaveBeenCalledWith(false, {
        ids: [editedOffer.id],
        isActive: true,
      })
      await waitForElementToBeRemoved(() => screen.getByRole('button', { name: "Activer l'offre" }))
      expect(screen.getByRole('button', { name: "Désactiver l'offre" })).toBeInTheDocument()
    })

    it('should allow to deactivate active offer', async () => {
      // Given
      pcapi.updateOffersActiveStatus.mockReturnValue(Promise.resolve())
      pcapi.loadOffer
        .mockResolvedValueOnce({ ...editedOffer, isActive: true })
        .mockResolvedValue({ ...editedOffer, isActive: false })
      await renderOfferDetails(props, store)

      // When
      fireEvent.click(screen.getByRole('button', { name: "Désactiver l'offre" }))

      // Then
      expect(pcapi.updateOffersActiveStatus).toHaveBeenCalledWith(false, {
        ids: [editedOffer.id],
        isActive: false,
      })
      await waitForElementToBeRemoved(() =>
        screen.getByRole('button', { name: "Désactiver l'offre" })
      )
      expect(screen.getByRole('button', { name: "Activer l'offre" })).toBeInTheDocument()
    })

    it('should not allow to deactivate pending offer', async () => {
      // Given
      pcapi.loadOffer.mockResolvedValue({ ...editedOffer, status: 'PENDING', isActive: true })

      // When
      await renderOfferDetails(props, store)

      // Then
      expect(screen.getByRole('button', { name: "Désactiver l'offre" })).toBeDisabled()
    })

    it('should not allow to deactivate rejected offer', async () => {
      // Given
      pcapi.loadOffer.mockResolvedValue({ ...editedOffer, status: 'REJECTED', isActive: false })

      // When
      await renderOfferDetails(props, store)

      // Then
      expect(screen.getByRole('button', { name: "Activer l'offre" })).toBeDisabled()
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
