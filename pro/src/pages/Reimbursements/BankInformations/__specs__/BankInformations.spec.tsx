import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import Notification from 'components/Notification/Notification'
import {
  ReimbursementContext,
  ReimbursementContextValues,
} from 'context/ReimbursementContext/ReimbursementContext'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import BankInformations from 'pages/Reimbursements/BankInformations/BankInformations'
import { defaultGetOffererResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

const renderBankInformations = (
  customContext: Partial<ReimbursementContextValues> = {},
  storeOverrides: any,
  initialRouterEntriesOverrides = '/remboursements/informations-bancaires'
) => {
  const contextValues: ReimbursementContextValues = {
    offerers: [],
    selectedOfferer: null,
    setOfferers: () => {},
    setSelectedOfferer: () => {},
    ...customContext,
  }

  renderWithProviders(
    <>
      <ReimbursementContext.Provider value={contextValues}>
        <BankInformations />
      </ReimbursementContext.Provider>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: [initialRouterEntriesOverrides],
    }
  )
}

const mockLogEvent = vi.fn()

describe('BankInformations page', () => {
  let store: any
  let customContext: Partial<ReimbursementContextValues>
  let offerer: GetOffererResponseModel

  beforeEach(() => {
    store = {
      user: {
        currentUser: {
          isAdmin: false,
        },
        initialized: true,
      },
    }

    offerer = {
      ...defaultGetOffererResponseModel,
      hasValidBankAccount: false,
    }

    customContext = {
      selectedOfferer: offerer,
      offerers: [
        {
          ...defaultGetOffererResponseModel,
          name: 'first offerer',
        },
        {
          ...defaultGetOffererResponseModel,
          id: 2,
          name: 'second offerer',
        },
      ],
    }

    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      id: 1,
      bankAccounts: [],
      managedVenues: [],
    })

    vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
  })

  it('should display not validated bank account message', async () => {
    renderBankInformations(customContext, store)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    expect(
      screen.getByText(
        'Ajoutez au moins un compte bancaire pour percevoir vos remboursements.'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
    expect(screen.getByText('En savoir plus')).toBeInTheDocument()
  })

  it('should render message when the user has a valid bank account and no pending one', async () => {
    if (customContext.selectedOfferer) {
      customContext.selectedOfferer = {
        ...customContext.selectedOfferer,
        hasValidBankAccount: true,
      }
    }
    renderBankInformations(customContext, store)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    expect(
      screen.queryByText(
        'Ajoutez au moins un compte bancaire pour percevoir vos remboursements.'
      )
    ).not.toBeInTheDocument()
    expect(
      screen.getByText(
        'Vous pouvez ajouter plusieurs comptes bancaires afin de percevoir les remboursements de vos offres. Chaque compte bancaire fera l’objet d’un remboursement et d’un justificatif de remboursement distincts.'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
    expect(screen.getByText('En savoir plus')).toBeInTheDocument()
  })

  it('should render message when has a pending bank account and no valid one', async () => {
    if (customContext.selectedOfferer) {
      customContext.selectedOfferer = {
        ...customContext.selectedOfferer,
        hasPendingBankAccount: true,
      }
    }
    renderBankInformations(customContext, store)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    expect(
      screen.queryByText(
        'Ajoutez au moins un compte bancaire pour percevoir vos remboursements.'
      )
    ).not.toBeInTheDocument()
    expect(
      screen.getByText(
        'Vous pouvez ajouter plusieurs comptes bancaires afin de percevoir les remboursements de vos offres. Chaque compte bancaire fera l’objet d’un remboursement et d’un justificatif de remboursement distincts.'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
    expect(screen.getByText('En savoir plus')).toBeInTheDocument()
  })

  it('should render default page if error on getOffererBankAccountsAndAttachedVenues request', async () => {
    vi.spyOn(
      api,
      'getOffererBankAccountsAndAttachedVenues'
    ).mockRejectedValueOnce({})

    renderBankInformations(customContext, store)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
    expect(api.getOffererBankAccountsAndAttachedVenues).toHaveBeenCalledTimes(1)
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    expect(
      screen.getByText(
        'Impossible de récupérer les informations relatives à vos comptes bancaires.'
      )
    ).toBeInTheDocument()
  })

  it('should render with default offerer select ', async () => {
    renderBankInformations(customContext, store)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.queryByText('Ajouter un compte bancaire')).toBeInTheDocument()

    expect(
      screen.queryByText(
        'Sélectionnez une structure pour faire apparaitre tous les comptes bancaires associés'
      )
    ).not.toBeInTheDocument()
  })

  it('should render with default offerer select', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        {
          id: 1,
          name: 'first offerer',
        },
        {
          id: 2,
          name: 'second offerer',
        },
      ],
    })
    renderBankInformations(customContext, store)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.queryByText('Ajouter un compte bancaire')).toBeInTheDocument()

    expect(
      screen.queryByText(
        'Sélectionnez une structure pour faire apparaitre tous les comptes bancaires associés'
      )
    ).not.toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
  })

  it('should show AddBankInformationsDialog on click add bank account button', async () => {
    renderBankInformations(customContext, store)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.queryByText(
        'Vous allez être redirigé vers le site demarches-simplifiees.fr'
      )
    ).not.toBeInTheDocument()

    await userEvent.click(await screen.findByText('Ajouter un compte bancaire'))

    expect(
      screen.getByText(
        'Vous allez être redirigé vers le site demarches-simplifiees.fr'
      )
    ).toBeInTheDocument()

    await userEvent.click(
      await screen.findByRole('button', { name: 'Fermer la modale' })
    )

    expect(
      screen.queryByText(
        'Vous allez être redirigé vers le site demarches-simplifiees.fr'
      )
    ).not.toBeInTheDocument()
  })

  it('should track add bank account button', async () => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderBankInformations(customContext, store)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    await userEvent.click(screen.getByText('Ajouter un compte bancaire'))
    expect(mockLogEvent).toHaveBeenCalledWith(
      BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT,
      {
        from: '/remboursements/informations-bancaires',
        offererId: 1,
      }
    )
  })
})
