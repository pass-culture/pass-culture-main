import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'

import AddBankInformationsDialog from '../AddBankInformationsDialog'

const mockLogEvent = vi.fn()

describe('AddBankInformations', () => {
  it('should render dialog', () => {
    render(<AddBankInformationsDialog closeDialog={vi.fn()} offererId={0} />)

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
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    render(<AddBankInformationsDialog closeDialog={vi.fn()} offererId={0} />)

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
