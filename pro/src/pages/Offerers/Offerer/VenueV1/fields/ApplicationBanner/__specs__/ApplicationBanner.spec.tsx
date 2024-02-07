import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import ApplicationBanner from '../ApplicationBanner'

describe('when offerer has no bank informations', () => {
  it('should render current application detail', async () => {
    // Given
    const props = {
      applicationId: '12',
    }

    // when
    renderWithProviders(<ApplicationBanner {...props} />)
    expect(
      await screen.findByText(
        'Les coordonnées bancaires de votre lieu sont en cours de validation par notre service financier. Vos remboursements seront rétroactifs une fois vos coordonnées bancaires validées.'
      )
    ).toBeInTheDocument()
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute(
      'href',
      'https://www.demarches-simplifiees.fr/dossiers/12/messagerie'
    )
    expect(link).toHaveTextContent('Voir le dossier en cours')
  })
})
