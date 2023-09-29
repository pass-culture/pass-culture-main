import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import Notification from 'components/Notification/Notification'
import {
  ReimbursementContext,
  ReimbursementContextValues,
} from 'context/ReimbursementContext/ReimbursementContext'
import { defautGetOffererResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import BankInformations from '../BankInformations'

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
        <Routes>
          <Route
            path="/remboursements/informations-bancaires"
            element={<BankInformations />}
          />
          <BankInformations />
        </Routes>
      </ReimbursementContext.Provider>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: [initialRouterEntriesOverrides],
    }
  )
}

describe('BankInformations page', () => {
  let store: any
  let customContext: Partial<ReimbursementContextValues>

  beforeEach(() => {
    store = {
      user: {
        currentUser: {
          isAdmin: false,
        },
        initialized: true,
      },
    }

    customContext = {
      selectedOfferer: {
        ...defautGetOffererResponseModel,
        hasValidBankAccount: false,
      },
      offerers: [
        {
          ...defautGetOffererResponseModel,
        },
        {
          ...defautGetOffererResponseModel,
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
  })

  it('should not display validated bank account message', async () => {
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
    expect(screen.queryByLabelText('Structure')).not.toBeInTheDocument()
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
    expect(
      screen.getByDisplayValue('Sélectionnez une structure')
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Sélectionnez une structure pour faire apparaitre tous les comptes bancaires associés'
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Ajouter un compte bancaire')
    ).not.toBeInTheDocument()

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
      store,
      '/remboursements/informations-bancaires?struture=2'
    )
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
    expect(screen.getByText('second offerer')).toBeInTheDocument()
  })
})
