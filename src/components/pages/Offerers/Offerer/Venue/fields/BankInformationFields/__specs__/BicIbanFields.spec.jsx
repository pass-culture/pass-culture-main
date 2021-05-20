import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'

import { BicIbanFields } from '../BicIbanFields'

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/venue/demarchesSimplifiees/procedure',
}))

const renderBicIbanFields = async props => {
  return await act(async () => {
    await render(<BicIbanFields {...props} />)
  })
}

describe('src | Venue | BicIbanFields', () => {
  it('should display bank informations', async () => {
    // Given
    const props = {
      bic: '123 456 789',
      iban: 'FRBICAVECUNEVALEURPARDEFAUT',
    }
    await renderBicIbanFields(props)

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
