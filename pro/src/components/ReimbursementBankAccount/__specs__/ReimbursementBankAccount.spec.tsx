import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import {
  BankAccountApplicationStatus,
  BankAccountResponseModel,
} from 'apiClient/v1'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import ReimbursementBankAccount from '../ReimbursementBankAccount'

const mockLogEvent = vi.fn()

const renderReimbursementBankAccount = (
  bankAccount: BankAccountResponseModel,
  venuesNotLinkedLength = 0,
  bankAccountsNumber = 1,
  offererId = 0
) =>
  renderWithProviders(
    <Routes>
      <Route
        path="/remboursements/informations-bancaires"
        element={
          <ReimbursementBankAccount
            bankAccount={bankAccount}
            venuesNotLinkedLength={venuesNotLinkedLength}
            bankAccountsNumber={bankAccountsNumber}
            offererId={offererId}
          />
        }
      />
    </Routes>,
    {
      storeOverrides: {},
      initialRouterEntries: ['/remboursements/informations-bancaires'],
    }
  )

describe('ReimbursementBankAccount', () => {
  let bankAccount: BankAccountResponseModel

  beforeEach(() => {
    bankAccount = {
      id: 1,
      isActive: true,
      label: 'Bank account label',
      obfuscatedIban: 'XXXX XXXX XXXX 0637',
      bic: 'BDFEFRPP',
      dsApplicationId: 6,
      status: BankAccountApplicationStatus.ACCEPTE,
      dateCreated: '2023-09-22T12:44:05.410448',
      dateLastStatusUpdate: null,
      linkedVenues: [{ id: 315, commonName: 'Le Petit Rintintin' }],
    }
  })

  it('should render with pending bank account if status is in draft', () => {
    bankAccount.status = BankAccountApplicationStatus.EN_CONSTRUCTION
    renderReimbursementBankAccount(bankAccount)

    expect(screen.getByText('Bank account label')).toBeInTheDocument()
    expect(screen.getByText('IBAN : **** 0637')).toBeInTheDocument()
    expect(screen.getByText('BIC : BDFEFRPP')).toBeInTheDocument()

    expect(
      screen.getByText(
        'Compte bancaire en cours de validation par nos services'
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Lieu(x) rattaché(s) à ce compte bancaire')
    ).not.toBeInTheDocument()
  })

  it('should render with pending bank account if status is on going', () => {
    bankAccount.status = BankAccountApplicationStatus.EN_INSTRUCTION
    renderReimbursementBankAccount(bankAccount)

    expect(screen.getByText('Bank account label')).toBeInTheDocument()
    expect(screen.getByText('IBAN : **** 0637')).toBeInTheDocument()
    expect(screen.getByText('BIC : BDFEFRPP')).toBeInTheDocument()

    expect(
      screen.getByText(
        'Compte bancaire en cours de validation par nos services'
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Lieu(x) rattaché(s) à ce compte bancaire')
    ).not.toBeInTheDocument()
  })

  it('should not render venues linked to bank account with only one bank account', () => {
    bankAccount.linkedVenues = []
    renderReimbursementBankAccount(bankAccount, 1)

    expect(
      screen.queryByText(
        'Compte bancaire en cours de validation par nos services'
      )
    ).not.toBeInTheDocument()

    expect(
      screen.getByText('Lieu(x) rattaché(s) à ce compte bancaire')
    ).toBeInTheDocument()

    expect(
      screen.getByText("Aucun lieu n'est rattaché à ce compte bancaire.")
    ).toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: 'Rattacher un lieu' })
    ).toBeInTheDocument()
  })

  it('should render without venues linked to bank account and with all venues linked to another account', () => {
    bankAccount.linkedVenues = []
    renderReimbursementBankAccount(bankAccount, 0, 2)

    expect(
      screen.getByText(
        "Aucun lieu n'est rattaché à ce compte bancaire. Désélectionnez un lieu déjà rattaché et rattachez-le à ce compte bancaire."
      )
    ).toBeInTheDocument()
  })

  it('should render with one venue not linked to bank account', () => {
    renderReimbursementBankAccount(bankAccount, 1, 2)

    expect(
      screen.getByText("Un de vos lieux n'est pas rattaché.")
    ).toBeInTheDocument()

    expect(
      screen.getByRole('img', { name: 'Une action est requise' })
    ).toBeInTheDocument()
    expect(screen.getByText('Le Petit Rintintin')).toBeInTheDocument()

    expect(screen.getByRole('button', { name: 'Modifier' })).toBeInTheDocument()
  })

  it('should render with several venues not linked to bank account', () => {
    renderReimbursementBankAccount(bankAccount, 2, 1)

    expect(
      screen.queryByText("Aucun lieu n'est rattaché à ce compte bancaire.")
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText(
        "Aucun lieu n'est rattaché à ce compte bancaire. Désélectionnez un lieu déjà rattaché et rattachez-le à ce compte bancaire."
      )
    ).not.toBeInTheDocument()

    expect(
      screen.getByText('Certains de vos lieux ne sont pas rattachés')
    ).toBeInTheDocument()
    expect(screen.getByText('Le Petit Rintintin')).toBeInTheDocument()

    expect(screen.getByRole('button', { name: 'Modifier' })).toBeInTheDocument()
  })

  it('should render with several venues not linked to bank account', () => {
    renderReimbursementBankAccount(bankAccount, 2, 1)

    expect(
      screen.getByText('Certains de vos lieux ne sont pas rattachés')
    ).toBeInTheDocument()
  })

  it('should display error icon if one or more venues are not linked to an account', () => {
    bankAccount.linkedVenues = []
    renderReimbursementBankAccount(bankAccount, 2, 1)

    expect(
      screen.getByRole('img', { name: 'Une action est requise' })
    ).toBeInTheDocument()
  })

  it('should not render error and warning messages when all venues are linked', () => {
    renderReimbursementBankAccount(bankAccount)

    expect(
      screen.queryByRole('img', { name: 'Une action est requise' })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText("Aucun lieu n'est rattaché à ce compte bancaire.")
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText(
        "Aucun lieu n'est rattaché à ce compte bancaire. Désélectionnez un lieu déjà rattaché et rattachez-le à ce compte bancaire."
      )
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText("Un de vos lieux n'est pas rattaché.")
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText('Certains de vos lieux ne sont pas rattachés')
    ).not.toBeInTheDocument()
  })

  it('should track attach venue button click', async () => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    bankAccount.linkedVenues = []
    renderReimbursementBankAccount(bankAccount, 1)

    await userEvent.click(
      screen.getByRole('button', { name: 'Rattacher un lieu' })
    )
    expect(mockLogEvent).toHaveBeenCalledWith(
      BankAccountEvents.CLICKED_ADD_VENUE_TO_BANK_ACCOUNT,
      {
        from: '/remboursements/informations-bancaires',
        offererId: 0,
      }
    )
  })
})
