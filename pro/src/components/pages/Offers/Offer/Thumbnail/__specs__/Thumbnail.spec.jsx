import '@testing-library/jest-dom'

import { fireEvent, screen, waitFor } from '@testing-library/react'

import {
  createFile,
  createImageFile,
  renderThumbnail,
} from 'components/pages/Offers/Offer/Thumbnail/__specs__/setup'
import {
  CANVAS_HEIGHT,
  CANVAS_WIDTH,
  CROP_BORDER_COLOR,
  CROP_BORDER_HEIGHT,
  CROP_BORDER_WIDTH,
} from 'components/pages/Offers/Offer/Thumbnail/_constants'
import CanvasTools from 'new_components/ImageEditor/canvas.js'

jest.mock('new_components/ImageEditor/canvas.js')

describe('thumbnail edition', () => {
  describe('when thumbnail exists', () => {
    it('should display a modal when the user is clicking on thumbnail', () => {
      // When
      renderThumbnail()

      // Then
      expect(screen.getByLabelText('Ajouter une image')).toBeInTheDocument()
      expect(
        screen.getByTitle('Fermer la modale', { selector: 'button' })
      ).toBeInTheDocument()
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
          screen.getByText(
            'Utilisez de préférence un visuel en orientation portrait',
            {
              selector: 'figcaption',
            }
          )
        ).toBeInTheDocument()
        const fileInput = screen.getByLabelText(
          'Importer une image depuis l’ordinateur'
        )
        expect(fileInput).toHaveAttribute('type', 'file')
        expect(fileInput).toHaveAttribute('accept', 'image/png,image/jpeg')
        expect(
          screen.getByText('Formats supportés : JPG, PNG', {
            selector: 'li',
          })
        ).toBeInTheDocument()
        expect(
          screen.getByText('Poids maximal du fichier : 10 Mo', {
            selector: 'li',
          })
        ).toBeInTheDocument()
        expect(
          screen.getByText('Largeur minimale de l’image : 400 px', {
            selector: 'li',
          })
        ).toBeInTheDocument()
      })

      it('should display advices for a good image', () => {
        // Given
        renderThumbnail()

        // When
        fireEvent.click(
          screen.getByText('Conseils pour votre image', { selector: 'button' })
        )

        // Then
        expect(
          screen.getByText(
            'Pour maximiser vos chances de réservations, choisissez avec soin l’image qui accompagne votre offre. Les ressources suivantes sont à votre disposition :'
          )
        ).toBeInTheDocument()
        expect(
          screen.getByText('Banques d’images libres de droits')
        ).toBeInTheDocument()
        const pexelsLink = screen.getByRole('link', {
          name: 'Pexels (nouvel onglet)',
        })
        expect(pexelsLink).toHaveAttribute(
          'href',
          'https://www.pexels.com/fr-fr/'
        )
        expect(pexelsLink).toHaveAttribute('rel', 'noopener noreferrer')
        expect(pexelsLink).toHaveAttribute('target', '_blank')
        const pixabayLink = screen.getByRole('link', {
          name: 'Pixabay (nouvel onglet)',
        })
        expect(pixabayLink).toHaveAttribute('href', 'https://pixabay.com/fr/')
        expect(pixabayLink).toHaveAttribute('rel', 'noopener noreferrer')
        expect(pixabayLink).toHaveAttribute('target', '_blank')
        const shutterstockLink = screen.getByRole('link', {
          name: 'Shutterstock (nouvel onglet)',
        })
        expect(shutterstockLink).toHaveAttribute(
          'href',
          'https://www.shutterstock.com/'
        )
        expect(shutterstockLink).toHaveAttribute('rel', 'noopener noreferrer')
        expect(shutterstockLink).toHaveAttribute('target', '_blank')
      })

      describe('and is selecting and image', () => {
        it('should display no error if file respects all rules', async () => {
          // Given
          renderThumbnail()
          const file = createImageFile()

          // When
          fireEvent.change(
            screen.getByLabelText('Importer une image depuis l’ordinateur'),
            {
              target: { files: [file] },
            }
          )

          // Then
          await waitFor(() => {
            expect(
              screen.queryByText('Formats supportés : JPG, PNG', {
                selector: 'strong',
              })
            ).not.toBeInTheDocument()
            expect(
              screen.queryByText('Poids maximal du fichier : 10 Mo', {
                selector: 'strong',
              })
            ).not.toBeInTheDocument()
            expect(
              screen.queryByText('Largeur minimale de l’image : 400 px', {
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
          fireEvent.change(
            screen.getByLabelText('Importer une image depuis l’ordinateur'),
            {
              target: { files: [file] },
            }
          )

          // Then
          await expect(
            screen.findByText('Formats supportés : JPG, PNG', {
              selector: 'strong',
            })
          ).resolves.toBeInTheDocument()
        })

        it('should display all the encountered validation errors', async () => {
          // Given
          renderThumbnail()
          const file = createFile({ sizeInMB: 50 })

          // When
          fireEvent.change(
            screen.getByLabelText('Importer une image depuis l’ordinateur'),
            {
              target: { files: [file] },
            }
          )

          // Then
          await waitFor(() => {
            expect(
              screen.getByText('Formats supportés : JPG, PNG', {
                selector: 'strong',
              })
            ).toBeInTheDocument()
            expect(
              screen.queryByText('Poids maximal du fichier : 10 Mo', {
                selector: 'strong',
              })
            ).toBeInTheDocument()
          })
        })

        it('should not import an image which exceeds maximum size', async () => {
          // Given
          renderThumbnail()
          const bigFile = createImageFile({ sizeInMB: 10 })

          // When
          fireEvent.change(
            screen.getByLabelText('Importer une image depuis l’ordinateur'),
            {
              target: { files: [bigFile] },
            }
          )

          // Then
          await expect(
            screen.findByText('Poids maximal du fichier : 10 Mo', {
              selector: 'strong',
            })
          ).resolves.toBeInTheDocument()
        })

        it('should not import an image whose width is below minimum', async () => {
          // Given
          renderThumbnail()
          const file = createImageFile({ width: 200 })

          // When
          fireEvent.change(
            screen.getByLabelText('Importer une image depuis l’ordinateur'),
            {
              target: { files: [file] },
            }
          )

          // Then
          await expect(
            screen.findByText('Largeur minimale de l’image : 400 px', {
              selector: 'strong',
            })
          ).resolves.toBeInTheDocument()
        })
      })
    })

    describe('when the user is on the credit step', () => {
      it('should display the credit step infos', async () => {
        // Given
        renderThumbnail()
        const file = createImageFile()

        // When
        fireEvent.change(
          screen.getByLabelText('Importer une image depuis l’ordinateur'),
          {
            target: { files: [file] },
          }
        )

        // Then
        await expect(
          screen.findByText('Crédit image et droits d’utilisation')
        ).resolves.toBeInTheDocument()
        await expect(
          screen.findByText('Crédit image')
        ).resolves.toBeInTheDocument()
        const inputCredit = await screen.findByPlaceholderText('Photographe...')
        expect(inputCredit.maxLength).toBe(255)
        await expect(
          screen.findByText(
            'En utilisant ce contenu, je certifie que je suis propriétaire ou que je dispose des autorisations nécessaires pour l’utilisation de celui-ci'
          )
        ).resolves.toBeInTheDocument()
        await expect(
          screen.findByText('Retour', { selector: 'button' })
        ).resolves.toBeInTheDocument()
        await expect(
          screen.findByText('Suivant', { selector: 'button' })
        ).resolves.toBeInTheDocument()
      })

      it('should return to the previous page if the return button is clicked', async () => {
        // Given
        renderThumbnail()
        const file = createImageFile()
        fireEvent.change(
          screen.getByLabelText('Importer une image depuis l’ordinateur'),
          {
            target: { files: [file] },
          }
        )

        // When
        fireEvent.click(
          await screen.findByText('Retour', { selector: 'button' })
        )

        // Then
        expect(
          screen.getByLabelText('Importer une image depuis l’ordinateur')
        ).toBeInTheDocument()
      })
    })

    describe('when the user is on the crop step', () => {
      it('should display the crop step infos', async () => {
        // Given
        renderThumbnail()
        const file = createImageFile()
        fireEvent.change(
          screen.getByLabelText('Importer une image depuis l’ordinateur'),
          {
            target: { files: [file] },
          }
        )

        // When
        fireEvent.click(
          await screen.findByText('Suivant', { selector: 'button' })
        )

        // Then
        expect(screen.getByText('Recadrer votre image')).toBeInTheDocument()
        expect(screen.getByText('Zoom')).toBeInTheDocument()
        expect(screen.getByRole('slider')).toBeInTheDocument()
        expect(screen.getByText('min')).toBeInTheDocument()
        expect(screen.getByText('max')).toBeInTheDocument()
        expect(
          screen.getByText('Retour', { selector: 'button' })
        ).toBeInTheDocument()
        expect(
          screen.getByText('Prévisualiser', { selector: 'button' })
        ).toBeInTheDocument()
      })

      it('should return to the credit step and the user must see the previous credit', async () => {
        // Given
        renderThumbnail()
        const file = createImageFile()
        fireEvent.change(
          screen.getByLabelText('Importer une image depuis l’ordinateur'),
          {
            target: { files: [file] },
          }
        )
        fireEvent.change(await screen.findByPlaceholderText('Photographe...'), {
          target: { value: 'A fake credit' },
        })
        fireEvent.click(
          await screen.findByText('Suivant', { selector: 'button' })
        )

        // When
        fireEvent.click(screen.getByText('Retour', { selector: 'button' }))

        // Then
        expect(screen.getByDisplayValue('A fake credit')).toBeInTheDocument()
      })

      it('should update the cropping border at each zoom', async () => {
        // Given
        renderThumbnail()
        const file = createImageFile()
        fireEvent.change(
          screen.getByLabelText('Importer une image depuis l’ordinateur'),
          {
            target: { files: [file] },
          }
        )
        fireEvent.change(await screen.findByPlaceholderText('Photographe...'), {
          target: { value: 'A fake credit' },
        })
        fireEvent.click(
          await screen.findByText('Suivant', { selector: 'button' })
        )

        // When
        fireEvent.change(screen.getByRole('slider'), { target: { value: 2.3 } })

        // Then
        expect(CanvasTools.mock.instances[0].drawArea).toHaveBeenCalledWith({
          width: 0,
          color: CROP_BORDER_COLOR,
          coordinates: [
            CROP_BORDER_WIDTH,
            CROP_BORDER_HEIGHT,
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
          ],
        })
      })
    })
  })
})
