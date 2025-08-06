import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'

import { api } from '@/apiClient//api'
import {
  BankAccountApplicationStatus,
  BankAccountResponseModel,
} from '@/apiClient//v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  defaultGetOffererResponseModel,
  defaultManagedVenues,
} from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { BankInformations } from '@/pages/Reimbursements/BankInformations/BankInformations'
import { ReimbursementsContextProps } from '@/pages/Reimbursements/Reimbursements'

const defaultBankAccountResponseModel: BankAccountResponseModel = {
  bic: 'bic',
  dateCreated: '2020-05-07',
  dsApplicationId: 1,
  id: 1,
  isActive: true,
  label: 'jacob',
  linkedVenues: [
    {
      commonName: 'carefully',
      id: 1,
    },
  ],
  obfuscatedIban: 'XXXX-123',
  status: BankAccountApplicationStatus.ACCEPTE,
}

const mockLogEvent = vi.fn()

const contextData: ReimbursementsContextProps = {
  selectedOfferer: {
    ...defaultGetOffererResponseModel,
    name: 'toto',
    id: 1,
  },
}
vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useOutletContext: () => contextData,
}))

function renderBankInformations() {
  renderWithProviders(<BankInformations />, {
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory(),
    },
  })
}

describe('BankInformations', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      bankAccounts: [defaultBankAccountResponseModel],
      id: 1,
      managedVenues: [
        {
          ...defaultManagedVenues,
          commonName: 'wanted',
        },
      ],
    })
  })

  it('should display the bank account section', async () => {
    renderBankInformations()

    expect(
      await screen.findByRole('button', {
        name: /Modifier/i,
      })
    ).toBeInTheDocument()
  })

  it('should display discard dialog on cancel', async () => {
    renderBankInformations()

    await userEvent.click(
      await screen.findByRole('button', {
        name: 'Modifier',
      })
    )

    expect(
      await screen.findByText(
        /Sélectionnez les structures dont les offres seront remboursées sur ce compte bancaire/
      )
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('wanted'))

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Annuler',
      })
    )

    expect(
      screen.queryByText(
        /Les informations non sauvegardées ne seront pas prises en compte/
      )
    ).toBeInTheDocument()
  })

  it('should display unlink venues dialog', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderBankInformations()

    await userEvent.click(
      await screen.findByRole('button', {
        name: 'Modifier',
      })
    )

    await userEvent.click(screen.getByText('wanted'))

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Enregistrer',
      })
    )

    expect(
      screen.queryByText(
        /Attention : la ou les structures désélectionnées ne seront plus remboursées sur ce compte bancaire/
      )
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Confirmer',
      })
    )
    expect(mockLogEvent).toHaveBeenCalledWith(
      'HasClickedSaveVenueToBankAccount',
      expect.objectContaining({
        id: 1,
        HasUncheckedVenue: true,
      })
    )
  })

  it('should display the bank account section even without context', async () => {
    vi.spyOn(router, 'useOutletContext').mockReturnValue(undefined)

    renderBankInformations()

    expect(
      await screen.findByRole('button', {
        name: /Ajouter un compte bancaire/i,
      })
    ).toBeInTheDocument()
  })
})
