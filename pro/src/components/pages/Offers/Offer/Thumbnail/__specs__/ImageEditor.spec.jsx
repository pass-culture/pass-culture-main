import '@testing-library/jest-dom'

import { fireEvent, screen, waitFor } from '@testing-library/react'

import {
  createImageFile,
  renderThumbnail,
} from 'components/pages/Offers/Offer/Thumbnail/__specs__/setup'

// The tests files have been separated in two because this mock
// breaks other tests
// we haven't find a better workarount yet
jest.mock('react-avatar-editor', () => ({
  __esModule: true,
  default: () => {
    return {
      getImage: jest.fn(() => {
        return {
          toDataURL: jest.fn(() => ''),
        }
      }),
      getCroppingRect: jest.fn(() => {
        return {
          x: 0.23,
          y: 0.15,
          width: 0.27,
          height: 0.7,
        }
      }),
      render: jest.fn(),
    }
  },
}))

describe('when the user is on the preview step', () => {
  it('should display the preview step infos', async () => {
    // Given
    renderThumbnail()
    const file = createImageFile()
    fireEvent.change(
      screen.getByLabelText('Importer une image depuis l’ordinateur'),
      {
        target: { files: [file] },
      }
    )
    fireEvent.click(await screen.findByText('Suivant', { selector: 'button' }))

    // When
    fireEvent.click(screen.getByText('Prévisualiser', { selector: 'button' }))

    // Then
    expect(
      screen.getByText(
        'Prévisualisation de votre image dans l’application pass Culture'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Page d’accueil')).toBeInTheDocument()
    expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
    expect(
      screen.getByText('Retour', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.getByText('Valider', { selector: 'button' })
    ).toBeInTheDocument()
  })

  it('should return to the crop step', async () => {
    // Given
    renderThumbnail()
    const file = createImageFile()
    fireEvent.change(
      screen.getByLabelText('Importer une image depuis l’ordinateur'),
      {
        target: { files: [file] },
      }
    )
    fireEvent.click(await screen.findByText('Suivant', { selector: 'button' }))
    fireEvent.click(screen.getByText('Prévisualiser', { selector: 'button' }))

    // When
    fireEvent.click(screen.getByText('Retour', { selector: 'button' }))

    // Then
    expect(screen.getByText('Recadrer votre image')).toBeInTheDocument()
  })

  it('should save thumbnail and close the modal when finishing import from computer', async () => {
    // Given
    const closeModal = jest.fn()
    const setThumbnailInfo = jest.fn()
    renderThumbnail({
      setIsModalOpened: closeModal,
      setThumbnailInfo: setThumbnailInfo,
    })

    const file = createImageFile()
    fireEvent.change(
      screen.getByLabelText('Importer une image depuis l’ordinateur'),
      {
        target: { files: [file] },
      }
    )

    fireEvent.change(await screen.findByPlaceholderText('Photographe...'), {
      target: { value: 'Mon crédit' },
    })
    fireEvent.click(await screen.findByText('Suivant', { selector: 'button' }))

    fireEvent.click(screen.getByText('Prévisualiser', { selector: 'button' }))

    // When
    fireEvent.click(screen.getByText('Valider', { selector: 'button' }))

    // Then
    await waitFor(() => {
      expect(
        screen.queryByText(
          'Prévisualisation de votre image dans l’application pass Culture'
        )
      ).not.toBeInTheDocument()
    })
    expect(closeModal).toHaveBeenCalledWith(false)
    expect(setThumbnailInfo).toHaveBeenCalledWith({
      credit: 'Mon crédit',
      croppingRect: {
        x: 0.23,
        y: 0.15,
        width: 0.27,
        height: 0.7,
      },
      thumbnail: file,
    })
  })
})
