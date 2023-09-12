import { waitFor, screen } from '@testing-library/react'
import React from 'react'

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
  })

  it('should has not validated bank account message', async () => {
    renderBankInformations(store)

    await waitFor(() => {
      expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    })
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
