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
import BankInformations from 'pages/Reimbursements/BankInformations/BankInformations'
import { defaultGetOffererResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

const renderBankInformations = (
  customContext: Partial<ReimbursementContextValues> = {},
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
      initialRouterEntries: [initialRouterEntriesOverrides],
    }
  )
}

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
        "Vous pouvez ajouter plusieurs comptes bancaires afin de percevoir les remboursements de vos offres. Chaque compte bancaire fera l'objet d'un remboursement et d'un justificatif de remboursement distincts."
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
        "Vous pouvez ajouter plusieurs comptes bancaires afin de percevoir les remboursements de vos offres. Chaque compte bancaire fera l'objet d'un remboursement et d'un justificatif de remboursement distincts."
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

  it('should render with default offerer select and update render on select element', async () => {
    renderBankInformations(customContext, store)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    const selectInput = screen.getByTestId('select-input-offerer')
    expect(screen.getByDisplayValue('first offerer')).toBeInTheDocument()
    expect(screen.queryByText('Ajouter un compte bancaire')).toBeInTheDocument()

    await userEvent.selectOptions(selectInput, 'second offerer')

    expect(screen.getByText('second offerer')).toBeInTheDocument()

    expect(
      screen.queryByText(
        'Sélectionnez une structure pour faire apparaitre tous les comptes bancaires associés'
      )
    ).not.toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
  })

  it('should render select input with correct offerer if url has offerer parameter', async () => {
    renderBankInformations(
      customContext,
      '/remboursements/informations-bancaires?structure=2'
    )
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getOffererBankAccountsAndAttachedVenues).toHaveBeenCalledTimes(1)
    expect(screen.getByText('second offerer')).toBeInTheDocument()
  })

  it('should render with default offerer select and update render on select element', async () => {
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

    const selectInput = screen.getByTestId('select-input-offerer')
    expect(screen.getByDisplayValue('first offerer')).toBeInTheDocument()
    expect(screen.queryByText('Ajouter un compte bancaire')).toBeInTheDocument()

    await userEvent.selectOptions(selectInput, 'second offerer')

    expect(screen.getByText('second offerer')).toBeInTheDocument()

    expect(
      screen.queryByText(
        'Sélectionnez une structure pour faire apparaitre tous les comptes bancaires associés'
      )
    ).not.toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
  })

  it('should render select input with correct offerer if url has offerer parameter', async () => {
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
    renderBankInformations(
      customContext,
      '/remboursements/informations-bancaires?structure=2'
    )
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
    expect(screen.getByText('second offerer')).toBeInTheDocument()
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
})
