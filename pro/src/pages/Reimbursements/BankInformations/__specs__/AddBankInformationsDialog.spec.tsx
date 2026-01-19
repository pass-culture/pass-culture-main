import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import * as useIsCaledonian from '@/commons/hooks/useIsCaledonian'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AddBankInformationsDialog } from '../AddBankInformationsDialog'

const mockLogEvent = vi.fn()

vi.mock('@/commons/utils/config', async () => {
  return {
    ...(await vi.importActual('@/commons/utils/config')),
    DS_BANK_ACCOUNT_PROCEDURE_ID: 'https://ds.fr',
    DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID:
      'https://ds-nouvelle-caledonie.fr',
  }
})

describe('AddBankInformationsDialog', () => {
  it('should render dialog', () => {
    renderWithProviders(
      <AddBankInformationsDialog
        closeDialog={vi.fn()}
        offererId={0}
        isDialogOpen
      />
    )

    expect(
      screen.getByText(
        'Vous allez être redirigé vers le site demarche.numerique.gouv.fr'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Démarche Numérique est une plateforme sécurisée de démarches administratives en ligne qui permet de déposer votre dossier de compte bancaire.'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText('Continuer sur demarche.numerique.gouv.fr')
    ).toBeInTheDocument()
  })

  it('should track continue to ds', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderWithProviders(
      <AddBankInformationsDialog
        closeDialog={vi.fn()}
        offererId={0}
        isDialogOpen
      />
    )

    await userEvent.click(
      screen.getByText('Continuer sur demarche.numerique.gouv.fr')
    )

    expect(mockLogEvent).toHaveBeenCalledWith(
      BankAccountEvents.CLICKED_CONTINUE_TO_DS,
      {
        offererId: 0,
      }
    )
  })

  it('should use DS_NEW_CALEDONIA_BANK_ACCOUNT_PROCEDURE_ID if isCaledonian is true', () => {
    vi.spyOn(useIsCaledonian, 'useIsCaledonian').mockReturnValueOnce(true)

    renderWithProviders(
      <AddBankInformationsDialog
        closeDialog={vi.fn()}
        offererId={0}
        isDialogOpen
      />
    )

    const link = screen.getByRole('link', {
      name: 'Continuer sur demarche.numerique.gouv.fr',
    })

    expect(link).toHaveAttribute('href', 'https://ds-nouvelle-caledonie.fr')
  })

  it('should use DS_BANK_ACCOUNT_PROCEDURE_ID if isCaledonian is false', () => {
    vi.spyOn(useIsCaledonian, 'useIsCaledonian').mockReturnValueOnce(false)

    renderWithProviders(
      <AddBankInformationsDialog
        closeDialog={vi.fn()}
        offererId={0}
        isDialogOpen
      />
    )
    const link = screen.getByRole('link', {
      name: 'Continuer sur demarche.numerique.gouv.fr',
    })

    expect(link).toHaveAttribute('href', 'https://ds.fr')
  })
})
