import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'

import { MemoryRouter, Route } from 'react-router'
import { render, screen } from '@testing-library/react'

import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import OfferLayout from '../OfferLayout'
import { Provider } from 'react-redux'
import React from 'react'
import { api } from 'apiClient/api'
import { configureTestStore } from 'store/testUtils'
import userEvent from '@testing-library/user-event'

jest.mock('repository/pcapi/pcapi', () => ({
  updateOffersActiveStatus: jest.fn(),
  loadCategories: jest.fn(),
  getUserValidatedOfferersNames: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  getOfferer: jest.fn(),
}))

const renderOfferDetails = (store, url) => {
  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[url]}>
        <Route
          path={[
            '/offre/creation/individuel',
            '/offre/:offerId([A-Z0-9]+)/individuel',
          ]}
        >
          <OfferLayout />
          <NotificationContainer />
        </Route>
      </MemoryRouter>
    </Provider>
  )
}

describe('offerLayout', () => {
  let editedOffer
  let store
  let categories

  beforeEach(() => {
    store = configureTestStore({
      user: {
        currentUser: {
          publicName: 'François',
          isAdmin: false,
          email: 'email@example.com',
        },
      },
    })
    categories = {
      categories: [
        {
          id: 'ID',
          name: 'Musique',
          proLabel: 'Musique',
          appLabel: 'Musique',
          isSelectable: true,
        },
      ],
      subcategories: [
        {
          id: 'ID',
          name: 'Musique SubCat 1',
          categoryId: 'ID',
          isEvent: false,
          isDigital: false,
          isDigitalDeposit: false,
          isPhysicalDeposit: true,
          proLabel: 'Musique SubCat 1',
          appLabel: 'Musique SubCat 1',
          conditionalFields: ['author', 'musicType', 'performer'],
          canExpire: true,
          canBeDuo: false,
          isSelectable: true,
        },
      ],
    }
    jest.spyOn(api, 'getOffer')
    pcapi.loadCategories.mockResolvedValue(categories)
  })

  describe('render when editing an existing offer', () => {
    beforeEach(() => {
      editedOffer = {
        id: 'AB',
        name: 'My edited offer',
        status: 'SOLD_OUT',
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
        venue: {
          audioDisabilityCompliant: true,
          mentalDisabilityCompliant: true,
          motorDisabilityCompliant: true,
          visualDisabilityCompliant: true,
          withdrawalDetails: 'My edited withdrawal details',
          id: 'ID',
          publicName: 'venue',
          name: 'venue',
          managingOfferer: {
            id: 'ID',
            name: 'offerer name',
          },
        },
        subcategoryId: 'ID',
      }
      api.getOffer.mockResolvedValue(editedOffer)
    })

    it('should have title `Modifier l’offre`', async () => {
      // When
      renderOfferDetails(store, '/offre/AB/individuel/edition')

      // Then
      const title = await screen.findByText('Modifier l’offre', {
        selector: 'h1',
      })
      expect(title).toBeInTheDocument()
    })

    it('should allow to activate inactive offer', async () => {
      // Given
      pcapi.updateOffersActiveStatus.mockResolvedValue()
      api.getOffer
        .mockResolvedValueOnce({
          ...editedOffer,
          isActive: false,
          status: 'INACTIVE',
          name: 'offer 1',
        })
        .mockResolvedValueOnce({
          ...editedOffer,
          isActive: false,
          status: 'INACTIVE',
          name: 'offer 1',
        })
        .mockResolvedValue({
          ...editedOffer,
          isActive: true,
          status: 'ACTIVE',
          name: 'offer 2',
        })

      renderOfferDetails(store, '/offre/AB/individuel/edition')

      // When
      await userEvent.click(
        await screen.findByRole('button', { name: 'Activer' })
      )

      // Then
      expect(pcapi.updateOffersActiveStatus).toHaveBeenNthCalledWith(
        1,
        [editedOffer.id],
        true
      )
      expect(
        screen.queryByRole('button', { name: 'Activer' })
      ).not.toBeInTheDocument()
      expect(
        screen.getByText('L’offre a bien été activée.')
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Désactiver' })
      ).toBeInTheDocument()
    })

    it('should allow to deactivate active offer', async () => {
      // Given
      pcapi.updateOffersActiveStatus.mockResolvedValue()
      api.getOffer
        .mockResolvedValueOnce({
          ...editedOffer,
          isActive: true,
          status: 'ACTIVE',
        })
        .mockResolvedValueOnce({
          ...editedOffer,
          isActive: true,
          status: 'ACTIVE',
        })
        .mockResolvedValue({
          ...editedOffer,
          isActive: false,
          status: 'INACTIVE',
        })
      renderOfferDetails(store, '/offre/AB/individuel/edition')

      // When
      await userEvent.click(
        await screen.findByRole('button', { name: 'Désactiver' })
      )

      // Then
      expect(pcapi.updateOffersActiveStatus).toHaveBeenCalledWith(
        [editedOffer.id],
        false
      )
      expect(
        screen.queryByRole('button', { name: 'Désactiver' })
      ).not.toBeInTheDocument()
      expect(
        screen.getByText('L’offre a bien été désactivée.')
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Activer' })
      ).toBeInTheDocument()
    })

    it('should not allow to deactivate pending offer', async () => {
      // Given
      api.getOffer.mockResolvedValue({
        ...editedOffer,
        status: 'PENDING',
        isActive: true,
      })

      // When
      renderOfferDetails(store, '/offre/AB/individuel/edition')

      // Then
      expect(
        await screen.findByRole('button', { name: 'Désactiver' })
      ).toBeDisabled()
    })

    it('should not allow to deactivate rejected offer', async () => {
      // Given
      api.getOffer.mockResolvedValue({
        ...editedOffer,
        status: 'REJECTED',
        isActive: false,
      })

      // When
      renderOfferDetails(store, '/offre/AB/individuel/edition')

      // Then
      expect(
        await screen.findByRole('button', { name: 'Désactiver' })
      ).toBeDisabled()
    })

    it('should inform user something went wrong when impossible to toggle offer status', async () => {
      // Given
      api.getOffer.mockResolvedValue({
        ...editedOffer,
        isActive: true,
      })
      pcapi.updateOffersActiveStatus.mockRejectedValue()
      renderOfferDetails(store, '/offre/AB/individuel/edition')

      // When
      await userEvent.click(
        await screen.findByRole('button', { name: 'Désactiver' })
      )

      // Then
      await expect(
        screen.findByText(
          'Une erreur est survenue, veuillez réessayer ultérieurement.'
        )
      ).resolves.toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Désactiver' })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Activer' })
      ).not.toBeInTheDocument()
    })
  })

  describe('render when creating a new offer', () => {
    it('should have title "Créer une offre"', async () => {
      pcapi.getVenuesForOfferer.mockResolvedValue([
        { id: 'AB', publicName: 'venue', name: 'venue' },
      ])
      pcapi.getUserValidatedOfferersNames.mockResolvedValue([])

      // When
      renderOfferDetails(store, '/offre/creation/individuel')

      // Then
      expect(
        await screen.findByText('Créer une offre', { selector: 'h1' })
      ).toBeInTheDocument()
    })
  })
})
