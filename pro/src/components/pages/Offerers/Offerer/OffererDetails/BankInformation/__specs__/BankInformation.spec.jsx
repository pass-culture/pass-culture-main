import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import { Offerer } from '../../Offerer'
import BankInformation from '../BankInformation'

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/offerer/demarchesSimplifiees/procedure',
}))

describe('src | Offerer | BankInformation', () => {
  it('should render instruction block when BIC and IBAN are provided', () => {
    // given
    const offererWithBankInformation = new Offerer({
      id: 'AA',
      name: 'fake offerer name',
      address: 'fake address',
      bic: 'offererBic',
      iban: 'offererIban',
      demarchesSimplifieesApplicationId: '12',
    })

    // when
    render(<BankInformation offerer={offererWithBankInformation} />)

    expect(
      screen.getByText(
        'Les coordonnées bancaires ci-dessous seront attribuées à tous les lieux sans coordonnées bancaires propres :'
      )
    ).toBeInTheDocument()

    expect(screen.getByText('offererBic')).toBeInTheDocument()
    expect(screen.getByText('offererIban')).toBeInTheDocument()
    const links = screen.getAllByRole('link')
    expect(links[0]).toHaveAttribute(
      'href',
      'link/to/offerer/demarchesSimplifiees/procedure'
    )
    expect(links[0]).toHaveTextContent('Modifier')
    expect(links[1]).toHaveAttribute(
      'href',
      'https://passculture.zendesk.com/hc/fr/articles/4411992051601'
    )
    expect(links[1]).toHaveTextContent('En savoir plus sur les remboursements')
  })

  it('should render current application detail when demarchesSimplifieesApplicationId is provided', () => {
    // Given
    const offererWithoutBankInformation = new Offerer({
      id: 'AA',
      name: 'fake offerer name',
      address: 'fake address',
      bic: null,
      iban: null,
      demarchesSimplifieesApplicationId: '12',
    })

    render(<BankInformation offerer={offererWithoutBankInformation} />)

    const links = screen.getAllByRole('link')
    expect(links[0]).toHaveAttribute(
      'href',
      'https://www.demarches-simplifiees.fr/dossiers/12'
    )
    expect(links[0]).toHaveTextContent('Accéder au dossier')
    expect(links[1]).toHaveAttribute(
      'href',
      'https://passculture.zendesk.com/hc/fr/articles/4411992051601'
    )
    expect(links[1]).toHaveTextContent('En savoir plus sur les remboursements')
  })
})
