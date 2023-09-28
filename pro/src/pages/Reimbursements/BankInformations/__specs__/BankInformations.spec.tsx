import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import {
  ReimbursementContext,
  ReimbursementContextValues,
} from 'context/ReimbursementContext/ReimbursementContext'
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
    <ReimbursementContext.Provider value={contextValues}>
      <BankInformations />
    </ReimbursementContext.Provider>,
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
        address: null,
        apiKey: {
          maxAllowed: 0,
          prefixes: [],
        },
        city: 'city',
        dateCreated: '1010/10/10',
        demarchesSimplifieesApplicationId: null,
        hasAvailablePricingPoints: false,
        hasDigitalVenueAtLeastOneOffer: false,
        hasValidBankAccount: false,
        hasPendingBankAccount: false,
        venuesWithNonFreeOffersWithoutBankAccounts: [],
        isActive: false,
        isValidated: false,
        managedVenues: [],
        name: 'name',
        id: 10,
        postalCode: '123123',
        siren: null,
        dsToken: '',
      },
      offerers: [
        {
          id: 1,
          name: 'first offerer',
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

  it('should render message when hasValidBankAccount and not hasPendingBankAccount', async () => {
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

  it('should render message when hasPendingBankAccount && not hasValidBankAccount', async () => {
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
})
