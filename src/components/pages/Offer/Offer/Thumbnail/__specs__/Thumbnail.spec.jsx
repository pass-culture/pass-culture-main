import '@testing-library/jest-dom'
import { fireEvent } from '@testing-library/dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import ThumbnailDialog from 'components/pages/Offer/Offer/Thumbnail/ThumbnailDialog'
import * as pcapi from 'repository/pcapi/pcapi'

import { MIN_IMAGE_HEIGHT, MIN_IMAGE_WIDTH } from '../_constants'

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

const renderThumbnail = () => {
  render(
    <MemoryRouter>
      <ThumbnailDialog setIsModalOpened={jest.fn()} />
    </MemoryRouter>
  )
}

describe('thumbnail edition', () => {
  describe('when thumbnail exists', () => {
    it('should display a modal when the user is clicking on thumbnail', async () => {
      // When
      renderThumbnail()

      // Then
      expect(screen.getByLabelText('Ajouter une image')).toBeInTheDocument()
      expect(screen.getByTitle('Fermer la modale', { selector: 'button' })).toBeInTheDocument()
    })
  })

  describe('when the user is within the upload tunnel', () => {
    describe('when the user is on import tab', () => {
      Object.defineProperty(global, 'createImageBitmap', {
        writable: true,
        value: () => Promise.resolve({}),
      })

      it('should display information for importing', async () => {
        // When
        renderThumbnail()

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
        renderThumbnail()
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
        renderThumbnail()
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
        renderThumbnail()
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
        expect(
          screen.queryByText('Le poids du fichier ne doit pas dépasser 10 Mo', {
            selector: 'strong',
          })
        ).not.toBeInTheDocument()
      })

      it('should not import an image which exceeds maximum size', async () => {
        // Given
        renderThumbnail()
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
        renderThumbnail()
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
        renderThumbnail()
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
        renderThumbnail()

        // When
        fireEvent.click(screen.getByText('Utiliser une URL'))

        // Then
        expect(
          await screen.findByText('Utilisez de préférence un visuel en orientation portrait', {
            selector: 'p',
          })
        ).toBeInTheDocument()
        const urlInput = screen.getByLabelText('URL de l’image')
        expect(urlInput).toHaveAttribute('type', 'text')
        expect(urlInput).toHaveAttribute('placeholder', 'Ex : http://...')
        expect(screen.getByText('Valider', { selector: 'button' })).toHaveAttribute('disabled')
      })

      it('should enable submit button if there is a string', async () => {
        // Given
        renderThumbnail()
        fireEvent.click(screen.getByText('Utiliser une URL'))

        // When
        fireEvent.change(screen.getByLabelText('URL de l’image'), { target: { value: 'MEFA' } })

        // Then
        expect(screen.getByText('Valider', { selector: 'button' })).not.toHaveAttribute('disabled')
      })

      it('should display an error if the url does meet the requirements', async () => {
        // Given
        jest.spyOn(pcapi, 'getURLErrors').mockResolvedValue({ errors: ['API error message'] })
        renderThumbnail()

        fireEvent.click(screen.getByText('Utiliser une URL'))
        fireEvent.change(screen.getByLabelText('URL de l’image'), {
          target: { value: 'http://not-an-image' },
        })

        // When
        fireEvent.click(screen.getByText('Valider', { selector: 'button' }))

        // Then
        expect(await screen.findByText('Valider', { selector: 'button' })).toHaveAttribute(
          'disabled'
        )
        expect(
          await screen.findByText('API error message', { selector: 'pre' })
        ).toBeInTheDocument()
      })

      it('should display a generic error if the api did not send a valid response', async () => {
        // Given
        jest.spyOn(pcapi, 'getURLErrors').mockRejectedValue({})
        renderThumbnail()

        fireEvent.click(screen.getByText('Utiliser une URL'))
        fireEvent.change(screen.getByLabelText('URL de l’image'), {
          target: { value: 'http://not-an-image' },
        })

        // When
        fireEvent.click(screen.getByText('Valider', { selector: 'button' }))

        // Then
        expect(await screen.findByText('Valider', { selector: 'button' })).toHaveAttribute(
          'disabled'
        )
        expect(
          await screen.findByText('Une erreur est survenue', { selector: 'pre' })
        ).toBeInTheDocument()
      })

      it('should display a URL format error if URL format is invalid', async () => {
        // Given
        renderThumbnail()
        fireEvent.click(screen.getByText('Utiliser une URL'))
        fireEvent.change(screen.getByLabelText('URL de l’image'), {
          target: { value: 'htp://url_example.com' },
        })

        // When
        fireEvent.click(screen.getByText('Valider', { selector: 'button' }))

        // Then
        expect(screen.getByText('Format d’URL non valide', { selector: 'pre' })).toBeInTheDocument()
      })

      it('should not display a URL format error if URL format is valid', async () => {
        // Given
        renderThumbnail()
        fireEvent.click(screen.getByText('Utiliser une URL'))
        fireEvent.change(screen.getByLabelText('URL de l’image'), {
          target: { value: 'https://url_example.com' },
        })

        // When
        fireEvent.click(screen.getByText('Valider', { selector: 'button' }))

        // Then
        expect(screen.queryByText('Format d’URL non valide')).not.toBeInTheDocument()
      })
    })
  })
})
