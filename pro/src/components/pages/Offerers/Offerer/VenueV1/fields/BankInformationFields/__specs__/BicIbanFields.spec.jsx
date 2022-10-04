import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import { BicIbanFields } from '../BicIbanFields'

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/venue/demarchesSimplifiees/procedure',
}))

describe('src | Venue | BicIbanFields', () => {
  it('should display bank informations', () => {
    // Given
    const props = {
      bic: '123 456 789',
      iban: 'FRBICAVECUNEVALEURPARDEFAUT',
    }
    render(<BicIbanFields {...props} />)

    // then
    expect(
      screen.getByText(
        'Les remboursements des offres éligibles présentées dans ce lieu sont effectués sur le compte ci-dessous :'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('123 456 789')).toBeInTheDocument()
    expect(screen.getByText('FRBICAVECUNEVALEURPARDEFAUT')).toBeInTheDocument()
  })
})
