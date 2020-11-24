import '@testing-library/jest-dom'
import { fireEvent } from '@testing-library/dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import OfferDetailsContainer from '../OfferDetailsContainer'

jest.mock('repository/pcapi/pcapi', () => ({
  createOffer: jest.fn(),
  getValidatedOfferers: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  loadOffer: jest.fn(),
  loadTypes: jest.fn(),
}))

const renderOffers = (props, store, queryParams = '') => {
  return render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[{ pathname: '/offres/v2/ABC12/edition', search: queryParams }]}
      >
        <Route
          exact
          path="/offres/v2/:offerId/edition"
        >
          <OfferDetailsContainer {...props} />
        </Route>
      </MemoryRouter>
    </Provider>
  )
}

describe('offerDetails - Edition', () => {
  let editedOffer
  let offerers
  let store
  let types
  let venues

  beforeEach(() => {
    store = configureTestStore({ data: { users: [{ publicName: 'François', isAdmin: false }] } })

    types = [
      {
        conditionalFields: ['author', 'visa', 'stageDirector'],
        offlineOnly: true,
        onlineOnly: false,
        proLabel: 'Cinéma - projections et autres évènements',
        type: 'Event',
        value: 'EventType.CINEMA',
      },
      {
        conditionalFields: ['author', 'musicType', 'performer'],
        offlineOnly: false,
        onlineOnly: false,
        proLabel: 'Musique - concerts, festivals',
        type: 'Event',
        value: 'EventType.MUSIQUE',
      },
      {
        conditionalFields: ['author', 'showType', 'stageDirector', 'performer'],
        offlineOnly: true,
        onlineOnly: false,
        proLabel: 'Spectacle vivant',
        type: 'Event',
        value: 'EventType.SPECTACLE_VIVANT',
      },
      {
        conditionalFields: [],
        offlineOnly: false,
        onlineOnly: true,
        proLabel: 'Presse en ligne - abonnements',
        type: 'Thing',
        value: 'ThingType.PRESSE_ABO',
      },
      {
        conditionalFields: ['author', 'isbn'],
        offlineOnly: false,
        onlineOnly: false,
        proLabel: 'Livres papier ou numérique, abonnements lecture',
        type: 'Thing',
        value: 'ThingType.LIVRE_EDITION',
      },
      {
        conditionalFields: [],
        offlineOnly: false,
        onlineOnly: true,
        proLabel: 'Cinéma - vente à distance',
        type: 'Thing',
        value: 'ThingType.CINEMA_CARD',
      },
      {
        conditionalFields: ['speaker'],
        offlineOnly: true,
        onlineOnly: false,
        proLabel: 'Conférences, rencontres et découverte des métiers',
        type: 'Event',
        value: 'EventType.CONFERENCE_DEBAT_DEDICACE',
      },
    ]
    offerers = [
      {
        id: 'BA',
        name: 'La structure',
      },
      {
        id: 'BAC',
        name: "L'autre structure",
      },
    ]
    venues = [
      {
        id: 'AB',
        isVirtual: false,
        managingOffererId: offerers[0].id,
        name: 'Le lieu',
        offererName: 'La structure',
      },
      {
        id: 'ABC',
        isVirtual: false,
        managingOffererId: offerers[1].id,
        name: "L'autre lieu",
        offererName: "L'autre structure",
      },
      {
        id: 'ABCD',
        isVirtual: true,
        managingOffererId: offerers[1].id,
        name: "L'autre lieu (Offre numérique)",
        offererName: "L'autre structure",
      },
    ]
    editedOffer = {
      id: 'ABC12',
      name: 'My edited offer',
    }
    pcapi.loadOffer.mockResolvedValue(editedOffer)
    pcapi.loadTypes.mockResolvedValue(types)
    pcapi.getValidatedOfferers.mockResolvedValue(offerers)
    pcapi.getVenuesForOfferer.mockResolvedValue(venues)
  })

  describe('render when editing an existing offer', () => {
    it('should have title "Éditer une offre"', async () => {
      // When
      renderOffers({}, store)

      // Then
      const title = await screen.findByText('Éditer une offre', { selector: 'h1' })
      expect(title).toBeInTheDocument()
    })

    it("should have a preview link redirecting to the webapp's offer page", async () => {
      // When
      renderOffers({}, store)

      // Then
      const previewLink = await screen.findByText('Prévisualiser', { selector: 'a' })
      expect(previewLink).toBeInTheDocument()
      const expectedWebappUri = `offre/details/${editedOffer.id}`
      expect(previewLink).toHaveAttribute('href', expect.stringContaining(expectedWebappUri))
    })

    it("should have a preview link redirecting to the webapp's offer page with mediationId as parameter when an active mediation exists", async () => {
      // Given
      editedOffer.activeMediation = { id: 'CBA' }

      // When
      renderOffers({}, store)

      // Then
      const previewLink = await screen.findByText('Prévisualiser', { selector: 'a' })
      expect(previewLink).toBeInTheDocument()
      const expectedWebappUri = `offre/details/${editedOffer.id}/${editedOffer.activeMediation.id}`
      expect(previewLink).toHaveAttribute('href', expect.stringContaining(expectedWebappUri))
    })

    it('should have offer title input', async () => {
      // When
      renderOffers({}, store)

      // Then
      const titleInput = await screen.findByLabelText("Titre de l'offre")
      expect(titleInput).toBeInTheDocument()
    })

    it('should change title with typed value', async () => {
      // Given
      renderOffers({}, store)
      const titleInput = await screen.findByLabelText("Titre de l'offre")

      // When
      fireEvent.change(titleInput, { target: { value: 'Mon nouveau titre' } })

      // Then
      const newTitleValue = await screen.findByDisplayValue('Mon nouveau titre')
      expect(newTitleValue).toBeInTheDocument()
    })
  })
})
