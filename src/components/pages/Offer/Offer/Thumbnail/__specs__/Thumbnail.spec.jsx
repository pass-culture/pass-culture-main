import '@testing-library/jest-dom'
import { fireEvent } from '@testing-library/dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import OfferLayoutContainer from 'components/pages/Offer/Offer/OfferLayoutContainer'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { queryByTextTrimHtml } from 'utils/testHelpers'

jest.mock('repository/pcapi/pcapi', () => ({
  getValidatedOfferers: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  loadOffer: jest.fn(),
  loadTypes: jest.fn(),
}))

const renderThumbnail = async (props, store) => {
  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[{ pathname: '/offres/v2/ABC12/edition' }]}>
        <Route path="/offres/v2/:offerId([A-Z0-9]+)/">
          <OfferLayoutContainer {...props} />
        </Route>
      </MemoryRouter>
    </Provider>
  )

  fireEvent.click(await screen.findByTitle('Modifier l’image', { selector: 'button' }))
}

describe('thumbnail edition', () => {
  let editedOffer
  let offerers
  let store
  let types
  let venues

  beforeEach(() => {
    store = configureTestStore({ data: { users: [{ publicName: 'François', isAdmin: false }] } })
    types = []
    offerers = []
    venues = []
    editedOffer = {
      id: 'ABC12',
      name: 'My edited offer',
      thumbUrl: 'http://example.net/active-image.png',
    }
    pcapi.getValidatedOfferers.mockResolvedValue(offerers)
    pcapi.getVenuesForOfferer.mockResolvedValue(venues)
    pcapi.loadOffer.mockResolvedValue(editedOffer)
    pcapi.loadTypes.mockResolvedValue(types)
  })

  describe('when thumbnail exists', () => {
    it('should display a modal when the user is clicking on thumbnail', async () => {
      // When
      await renderThumbnail({}, store)

      // Then
      expect(screen.getByLabelText('Ajouter une image')).toBeInTheDocument()
      expect(screen.getByTitle('Fermer la modale', { selector: 'button' })).toBeInTheDocument()
    })
  })

  describe('when the user is within the upload tunnel', () => {
    it('should close the modal when user is clicking on close button', async () => {
      // Given
      await renderThumbnail({}, store)

      // When
      fireEvent.click(screen.getByTitle('Fermer la modale', { selector: 'button' }))

      // Then
      expect(screen.queryByLabelText('Ajouter une image')).not.toBeInTheDocument()
      expect(
        screen.queryByTitle('Fermer la modale', { selector: 'button' })
      ).not.toBeInTheDocument()
    })

    describe('when the user is on import tab', () => {
      it('should display information for importing', async () => {
        // When
        await renderThumbnail({}, store)

        // Then
        expect(
          screen.getByText('Utilisez de préférence un visuel en orientation portrait', {
            selector: 'p',
          })
        ).toBeInTheDocument()
        const input = screen.getByLabelText('Importer une image depuis l’ordinateur')
        expect(input).toHaveAttribute('type', 'file')
        expect(input).toHaveAttribute('accept', 'image/png, image/jpeg')
        expect(
          queryByTextTrimHtml(
            screen,
            'Format supportés : JPG, PNG Le poids du fichier de ne doit pas dépasser 10 Mo La taille de l’image doit être supérieure à 400 x 400px'
          )
        ).toBeInTheDocument()
      })
    })
  })
})
