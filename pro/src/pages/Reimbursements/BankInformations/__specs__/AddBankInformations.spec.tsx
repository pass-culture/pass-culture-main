import { render, screen } from '@testing-library/react'
import React from 'react'

import AddBankInformationsDialog from '../AddBankInformationsDialog'

describe('AddBankInformations', () => {
  it('should render dialog', () => {
    render(<AddBankInformationsDialog closeDialog={vi.fn()} />)

    expect(
      screen.getByText(
        'Vous allez être redirigé vers le site demarches-simplifiees.fr'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Démarches Simplifiées est une plateforme sécurisée de démarches administratives en ligne qui permet de déposer votre dossier de compte bancaire.'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText('Continuer sur demarches-simplifiees.fr')
    ).toBeInTheDocument()
  })
})
