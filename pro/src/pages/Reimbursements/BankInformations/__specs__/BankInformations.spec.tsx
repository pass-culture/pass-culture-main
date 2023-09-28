import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

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
  storeOverrides: any
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
      ],
    }

    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      id: 1,
      bankAccounts: [],
      managedVenues: [],
    })
  })

  it('should has not validated bank account message', async () => {
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
})
