import '@testing-library/jest-dom'
import { fireEvent, screen, waitFor } from '@testing-library/react'

import {
  createFile,
  createImageFile,
  renderThumbnail,
} from 'components/pages/Offer/Offer/Thumbnail/__specs__/setup'
import {
  CANVAS_HEIGHT,
  CANVAS_WIDTH,
  CROP_BORDER_COLOR,
  CROP_BORDER_HEIGHT,
  CROP_BORDER_WIDTH,
} from 'components/pages/Offer/Offer/Thumbnail/_constants'
import * as pcapi from 'repository/pcapi/pcapi'
import CanvasTools from 'utils/canvas.js'

jest.mock('utils/canvas.js')

describe('thumbnail edition', () => {
  describe('when thumbnail exists', () => {
    it('should display a modal when the user is clicking on thumbnail', () => {
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

      it('should display advices for a good image', () => {
        // Given
        renderThumbnail()

        // When
        fireEvent.click(screen.getByText('Conseils pour votre image', { selector: 'button' }))

        // Then
        expect(
          screen.getByText(
            'Pour maximiser vos chances de réservations, choisissez avec soin l’image qui accompagne votre offre. Les ressources suivantes sont à votre disposition :'
          )
        ).toBeInTheDocument()
        expect(screen.getByText('Banque d’images libre de droits')).toBeInTheDocument()
        const pexelsLink = screen.getByRole('link', { name: 'Pexels (nouvel onglet)' })
        expect(pexelsLink).toHaveAttribute('href', 'https://www.pexels.com/fr-fr/')
        expect(pexelsLink).toHaveAttribute('rel', 'noopener noreferrer')
        expect(pexelsLink).toHaveAttribute('target', '_blank')
        const pixabayLink = screen.getByRole('link', { name: 'Pixabay (nouvel onglet)' })
        expect(pixabayLink).toHaveAttribute('href', 'https://pixabay.com/fr/')
        expect(pixabayLink).toHaveAttribute('rel', 'noopener noreferrer')
        expect(pixabayLink).toHaveAttribute('target', '_blank')
        const shutterstockLink = screen.getByRole('link', { name: 'Shutterstock (nouvel onglet)' })
        expect(shutterstockLink).toHaveAttribute('href', 'https://www.shutterstock.com/')
        expect(shutterstockLink).toHaveAttribute('rel', 'noopener noreferrer')
        expect(shutterstockLink).toHaveAttribute('target', '_blank')
        expect(screen.getByText('Gabarits')).toBeInTheDocument()
        expect(
          screen.getByRole('link', { name: 'Gabarit Photoshop (.psd, 116 Ko)' })
        ).toBeInTheDocument()
        expect(
          screen.getByRole('link', { name: 'Gabarit Illustrator (.eps, 836 Ko)' })
        ).toBeInTheDocument()
      })

      describe('and is selecting and image', () => {
        it('should display no error if file respects all rules', async () => {
          // Given
          renderThumbnail()
          const file = createImageFile()

          // When
          fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
            target: { files: [file] },
          })

          // Then
          await waitFor(() => {
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
          await waitFor(() => {
            expect(
              screen.getByText('Formats supportés : JPG, PNG', {
                selector: 'strong',
              })
            ).toBeInTheDocument()
            expect(
              screen.queryByText('Le poids du fichier ne doit pas dépasser 10 Mo', {
                selector: 'strong',
              })
            ).not.toBeInTheDocument()
          })
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
          fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
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
          fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
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

      it('should enable submit button if there is a string', () => {
        // Given
        renderThumbnail()
        fireEvent.click(screen.getByText('Utiliser une URL'))

        // When
        fireEvent.change(screen.getByLabelText('URL de l’image'), { target: { value: 'MEFA' } })

        // Then
        expect(screen.getByText('Valider', { selector: 'button' })).not.toHaveAttribute('disabled')
      })

      it('should display an error if the url does not meet the requirements', async () => {
        // Given
        jest
          .spyOn(pcapi, 'validateDistantImage')
          .mockResolvedValue({ errors: ['API error message'] })
        renderThumbnail()

        fireEvent.click(screen.getByText('Utiliser une URL'))
        fireEvent.change(screen.getByLabelText('URL de l’image'), {
          target: { value: 'http://not-an-image' },
        })

        // When
        fireEvent.click(screen.getByText('Valider', { selector: 'button' }))

        // Then
        expect(screen.getByLabelText('URL de l’image')).toHaveAttribute('disabled')
        expect(await screen.findByText('Valider', { selector: 'button' })).toHaveAttribute(
          'disabled'
        )
        expect(
          await screen.findByText('API error message', { selector: 'pre' })
        ).toBeInTheDocument()
      })

      it('should display a generic error if the api did not send a valid response', async () => {
        // Given
        jest.spyOn(pcapi, 'validateDistantImage').mockRejectedValue({})
        renderThumbnail()

        fireEvent.click(screen.getByText('Utiliser une URL'))
        fireEvent.change(screen.getByLabelText('URL de l’image'), {
          target: { value: 'http://not-an-image' },
        })

        // When
        fireEvent.click(screen.getByText('Valider', { selector: 'button' }))

        // Then
        expect(screen.getByLabelText('URL de l’image')).toHaveAttribute('disabled')
        expect(await screen.findByText('Valider', { selector: 'button' })).toHaveAttribute(
          'disabled'
        )
        expect(
          await screen.findByText('Une erreur est survenue', { selector: 'pre' })
        ).toBeInTheDocument()
      })

      it('should display a URL format error if URL format is invalid', () => {
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
        await waitFor(() => {
          expect(screen.queryByText('Format d’URL non valide')).not.toBeInTheDocument()
        })
      })

      it('should remove the error if the user rewrite the URL after a first error', () => {
        // Given
        renderThumbnail()
        fireEvent.click(screen.getByText('Utiliser une URL'))
        fireEvent.change(screen.getByLabelText('URL de l’image'), {
          target: { value: 'htp://url_example.com' },
        })
        fireEvent.click(screen.getByText('Valider', { selector: 'button' }))

        // When
        fireEvent.change(screen.getByPlaceholderText('Ex : http://...'), {
          target: { value: 'http://url_example.com' },
        })

        // Then
        expect(
          screen.queryByText('Format d’URL non valide', { selector: 'pre' })
        ).not.toBeInTheDocument()
      })

      it('should go to the credit step if there is no validation error', async () => {
        // Given
        jest.spyOn(pcapi, 'validateDistantImage').mockResolvedValue({ errors: [] })
        renderThumbnail()
        fireEvent.click(screen.getByText('Utiliser une URL'))
        fireEvent.change(screen.getByLabelText('URL de l’image'), {
          target: { value: 'http://url_example.com' },
        })

        // When
        fireEvent.click(screen.getByText('Valider', { selector: 'button' }))

        // Then
        expect(await screen.findByText('Crédit image et droits d’utilisation')).toBeInTheDocument()
      })
    })

    describe('when the user is on the credit step', () => {
      it('should display the credit step infos', async () => {
        // Given
        renderThumbnail()
        const file = createImageFile()

        // When
        fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
          target: { files: [file] },
        })

        // Then
        expect(await screen.findByText('Crédit image et droits d’utilisation')).toBeInTheDocument()
        expect(await screen.findByText('Crédit image')).toBeInTheDocument()
        const inputCredit = await screen.findByPlaceholderText('Photographe...')
        expect(inputCredit.maxLength).toBe(255)
        expect(
          await screen.findByText(
            'En utilisant ce contenu, je certifie que je suis propriétaire ou que je dispose des autorisations nécessaires pour l’utilisation de celui-ci'
          )
        ).toBeInTheDocument()
        expect(await screen.findByText('Retour', { selector: 'button' })).toBeInTheDocument()
        expect(await screen.findByText('Suivant', { selector: 'button' })).toBeInTheDocument()
      })

      it('should return to the previous page if the return button is clicked', async () => {
        // Given
        renderThumbnail()
        const file = createImageFile()
        fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
          target: { files: [file] },
        })

        // When
        fireEvent.click(await screen.findByText('Retour', { selector: 'button' }))

        // Then
        expect(screen.getByLabelText('Importer une image depuis l’ordinateur')).toBeInTheDocument()
      })
    })

    describe('when the user is on the crop step', () => {
      it('should display the crop step infos', async () => {
        // Given
        renderThumbnail()
        const file = createImageFile()
        fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
          target: { files: [file] },
        })

        // When
        fireEvent.click(await screen.findByText('Suivant', { selector: 'button' }))

        // Then
        expect(screen.getByText('Recadrer votre image')).toBeInTheDocument()
        expect(screen.getByLabelText('Zoom')).toBeInTheDocument()
        expect(screen.getByRole('slider')).toBeInTheDocument()
        expect(screen.getByText('min')).toBeInTheDocument()
        expect(screen.getByText('max')).toBeInTheDocument()
        expect(screen.getByText('Retour', { selector: 'button' })).toBeInTheDocument()
        expect(screen.getByText('Prévisualiser', { selector: 'button' })).toBeInTheDocument()
      })

      it('should return to the credit step and the user must see the previous credit', async () => {
        // Given
        renderThumbnail()
        const file = createImageFile()
        fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
          target: { files: [file] },
        })
        fireEvent.change(await screen.findByPlaceholderText('Photographe...'), {
          target: { value: 'A fake credit' },
        })
        fireEvent.click(await screen.findByText('Suivant', { selector: 'button' }))

        // When
        fireEvent.click(screen.getByText('Retour', { selector: 'button' }))

        // Then
        expect(screen.getByDisplayValue('A fake credit')).toBeInTheDocument()
      })

      it('should update the cropping border at each zoom', async () => {
        // Given
        renderThumbnail()
        const file = createImageFile()
        fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
          target: { files: [file] },
        })
        fireEvent.change(await screen.findByPlaceholderText('Photographe...'), {
          target: { value: 'A fake credit' },
        })
        fireEvent.click(await screen.findByText('Suivant', { selector: 'button' }))

        // When
        fireEvent.change(screen.getByRole('slider'), { target: { value: 2.3 } })

        // Then
        expect(CanvasTools.mock.instances[0].drawArea).toHaveBeenCalledWith({
          width: 0,
          color: CROP_BORDER_COLOR,
          coordinates: [CROP_BORDER_WIDTH, CROP_BORDER_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT],
        })
      })
    })
  })
})
