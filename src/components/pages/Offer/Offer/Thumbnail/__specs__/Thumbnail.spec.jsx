import '@testing-library/jest-dom'
import { fireEvent } from '@testing-library/dom'
import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import OfferLayoutContainer from 'components/pages/Offer/Offer/OfferLayoutContainer'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import { MIN_IMAGE_HEIGHT, MIN_IMAGE_WIDTH } from '../_constants'

global.createImageBitmap = () => Promise.resolve({})

const createImageFile = ({
  name = 'example.png',
  type = 'image/png',
  sizeInMB = 1,
  width = MIN_IMAGE_WIDTH,
  height = MIN_IMAGE_HEIGHT,
} = {}) => {
  const file = createFile({ name, type, sizeInMB })
  jest.spyOn(global, 'createImageBitmap').mockResolvedValue({ width, height })
  return file
}

const createFile = ({ name = 'example.json', type = 'application/json', sizeInMB = 1 } = {}) => {
  const oneMB = 1024 * 1024
  const file = new File([''], name, { type })
  Object.defineProperty(file, 'size', { value: oneMB * sizeInMB })
  return file
}

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

    const editedOfferVenue = {
      id: 'AB',
      managingOffererId: 'BA',
      name: 'Le lieu',
      offererName: 'La structure',
      managingOfferer: {
        id: 'BA',
        name: 'La structure',
      },
    }
    editedOffer = {
      id: 'ABC12',
      name: 'My edited offer',
      thumbUrl: 'http://example.net/active-image.png',
      type: 'ThingType.LIVRE_EDITION',
      venue: editedOfferVenue,
      venueId: editedOfferVenue.id,
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
        const fileInput = screen.getByLabelText('Importer une image depuis l’ordinateur')
        expect(fileInput).toHaveAttribute('type', 'file')
        expect(fileInput).toHaveAttribute('accept', 'image/png,image/jpeg')
        expect(
          screen.getByText('Formats supportés : JPG, PNG', {
            selector: 'li',
          })
        ).toBeInTheDocument()
        expect(
          screen.getByText('Le poids du fichier ne doit pas dépasser 10 Mo', {
            selector: 'li',
          })
        ).toBeInTheDocument()
        expect(
          screen.getByText('La taille de l’image doit être supérieure à 400 x 400px', {
            selector: 'li',
          })
        ).toBeInTheDocument()
      })

      it('should display no error if file respects all rules', async () => {
        // Given
        await renderThumbnail({}, store)
        const file = createImageFile()

        // When
        fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
          target: { files: [file] },
        })

        // Then
        expect(
          screen.queryByText('Formats supportés : JPG, PNG', {
            selector: 'strong',
          })
        ).not.toBeInTheDocument()
        expect(
          screen.queryByText('Le poids du fichier ne doit pas dépasser 10 Mo', {
            selector: 'strong',
          })
        ).not.toBeInTheDocument()
        expect(
          screen.queryByText('La taille de l’image doit être supérieure à 400 x 400px', {
            selector: 'strong',
          })
        ).not.toBeInTheDocument()
      })

      it('should not import a file other than png or jpg', async () => {
        // Given
        await renderThumbnail({}, store)
        const file = createFile()

        // When
        fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
          target: { files: [file] },
        })

        // Then
        expect(
          await screen.findByText('Formats supportés : JPG, PNG', {
            selector: 'strong',
          })
        ).toBeInTheDocument()
      })

      it('should only display the first encountered validation error', async () => {
        // Given
        await renderThumbnail({}, store)
        const file = createFile({ sizeInMB: 50 })

        // When
        fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
          target: { files: [file] },
        })

        // Then
        expect(
          await screen.findByText('Formats supportés : JPG, PNG', {
            selector: 'strong',
          })
        ).toBeInTheDocument()

        await waitFor(() => {
          expect(
            screen.queryByText('Le poids du fichier ne doit pas dépasser 10 Mo', {
              selector: 'strong',
            })
          ).not.toBeInTheDocument()
        })
      })

      it('should not import an image which exceeds maximum size', async () => {
        // Given
        await renderThumbnail({}, store)
        const bigFile = createImageFile({ sizeInMB: 10 })

        // When
        fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
          target: { files: [bigFile] },
        })

        // Then
        expect(
          await screen.findByText('Le poids du fichier ne doit pas dépasser 10 Mo', {
            selector: 'strong',
          })
        ).toBeInTheDocument()
      })

      it('should not import an image whose height is below minimum', async () => {
        // Given
        await renderThumbnail({}, store)
        const file = createImageFile({ height: 200 })

        // When
        await fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
          target: { files: [file] },
        })

        // Then
        expect(
          await screen.findByText('La taille de l’image doit être supérieure à 400 x 400px', {
            selector: 'strong',
          })
        ).toBeInTheDocument()
      })

      it('should not import an image whose width is below minimum', async () => {
        // Given
        await renderThumbnail({}, store)
        const file = createImageFile({ width: 200 })

        // When
        await fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
          target: { files: [file] },
        })

        // Then
        expect(
          await screen.findByText('La taille de l’image doit être supérieure à 400 x 400px', {
            selector: 'strong',
          })
        ).toBeInTheDocument()
      })
    })

    describe('when the user is on url tab', () => {
      it('should display information for importing', async () => {
        // Given
        await renderThumbnail({}, store)

        // When
        fireEvent.click(screen.getByText('Utiliser une URL'))

        // Then
        expect(
          await screen.findByText('Utilisez de préférence un visuel en orientation portrait', {
            selector: 'p',
          })
        ).toBeInTheDocument()
        const urlInput = screen.getByLabelText('URL de l’image')
        expect(urlInput).toHaveAttribute('type', 'url')
        expect(urlInput).toHaveAttribute('placeholder', 'Ex : http://...')
        expect(screen.getByText('Valider', { selector: 'button' })).toHaveAttribute('disabled')
      })

      it('should enable submit button if there is a string', async () => {
        // Given
        await renderThumbnail({}, store)
        fireEvent.click(screen.getByText('Utiliser une URL'))

        // When
        fireEvent.change(screen.getByLabelText('URL de l’image'), { target: { value: 'MEFA' } })

        // Then
        expect(screen.getByText('Valider', { selector: 'button' })).not.toHaveAttribute('disabled')
      })
    })
  })
})
