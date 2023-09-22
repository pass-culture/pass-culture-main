import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import BankInformations from '../BankInformations'

const renderBankInformations = async (storeOverrides: any) => {
  renderWithProviders(<BankInformations />, {
    storeOverrides,
  })
}

describe('BankInformations page', () => {
  let store: any

  beforeEach(() => {
    store = {
      user: {
        currentUser: {
          isAdmin: false,
        },
        initialized: true,
      },
    }

    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        {
          id: 1,
          name: 'first offerer',
        },
      ],
    })

    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      id: 1,
      bankAccounts: [],
      managedVenues: [],
    })
  })

  it('should has not validated bank account message', async () => {
    renderBankInformations(store)

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

  it('should render message when hasValidBankAccount and hasPendingBankAccount')
})
