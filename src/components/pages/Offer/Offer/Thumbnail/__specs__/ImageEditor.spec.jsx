import '@testing-library/jest-dom'
import { fireEvent, screen } from '@testing-library/react'

import {
  createImageFile,
  renderThumbnail,
} from 'components/pages/Offer/Offer/Thumbnail/__specs__/setup'

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
      render: jest.fn(),
    }
  },
}))

describe('when the user is on the preview step', () => {
  it('should display the preview step infos', async () => {
    // Given
    renderThumbnail()
    const file = createImageFile()
    fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
      target: { files: [file] },
    })
    fireEvent.click(await screen.findByText('Suivant', { selector: 'button' }))

    // When
    fireEvent.click(screen.getByText('Prévisualiser', { selector: 'button' }))

    // Then
    expect(
      screen.getByText('Prévisualisation de votre image dans l’application pass Culture')
    ).toBeInTheDocument()
    expect(screen.getByText('Page d’accueil')).toBeInTheDocument()
    expect(screen.getByText('Détail de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Retour', { selector: 'button' })).toBeInTheDocument()
    expect(screen.getByText('Valider', { selector: 'button' })).toBeInTheDocument()
  })

  it('should return to the crop step', async () => {
    // Given
    renderThumbnail()
    const file = createImageFile()
    fireEvent.change(screen.getByLabelText('Importer une image depuis l’ordinateur'), {
      target: { files: [file] },
    })
    fireEvent.click(await screen.findByText('Suivant', { selector: 'button' }))
    fireEvent.click(screen.getByText('Prévisualiser', { selector: 'button' }))

    // When
    fireEvent.click(screen.getByText('Retour', { selector: 'button' }))

    // Then
    expect(screen.getByText('Recadrer votre image')).toBeInTheDocument()
  })
})
