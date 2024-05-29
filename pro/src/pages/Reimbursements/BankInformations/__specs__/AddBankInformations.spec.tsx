import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import * as useAnalytics from 'app/App/analytics/firebase'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import { AddBankInformationsDialog } from '../AddBankInformationsDialog'

const mockLogEvent = vi.fn()

describe('AddBankInformations', () => {
  it('should render dialog', () => {
    renderWithProviders(
      <AddBankInformationsDialog closeDialog={vi.fn()} offererId={0} />
    )

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

  it('should track continue to ds', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderWithProviders(
      <AddBankInformationsDialog closeDialog={vi.fn()} offererId={0} />
    )

    await userEvent.click(
      screen.getByText('Continuer sur demarches-simplifiees.fr')
    )

    expect(mockLogEvent).toHaveBeenCalledWith(
      BankAccountEvents.CLICKED_CONTINUE_TO_DS,
      {
        offererId: 0,
      }
    )
  })
})
