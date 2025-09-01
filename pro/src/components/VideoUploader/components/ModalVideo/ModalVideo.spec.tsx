import { screen, waitFor } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ModalVideo } from './ModalVideo'

describe('ModalVideo', () => {
  it('should render an heading, a cancel button, a save button and a field', () => {
    renderWithProviders(<ModalVideo open={true} />)

    waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Ajouter une vidéo' })
      ).toBeInTheDocument()
    })

    expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ajouter' })).toBeInTheDocument()
    expect(screen.getByLabelText('Lien URL Youtube')).toBeInTheDocument()
  })
})
