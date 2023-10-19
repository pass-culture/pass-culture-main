import { render, screen } from '@testing-library/react'
import React from 'react'

import {
  BankAccountApplicationStatus,
  BankAccountResponseModel,
} from 'apiClient/v1'

import ReimbursementBankAccount from '../ReimbursementBankAccount'

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
    render(
      <ReimbursementBankAccount
        bankAccount={bankAccount}
        venuesNotLinkedLength={0}
        bankAccountsNumber={1}
      />
    )

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
    render(
      <ReimbursementBankAccount
        bankAccount={bankAccount}
        venuesNotLinkedLength={0}
        bankAccountsNumber={1}
      />
    )

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
    render(
      <ReimbursementBankAccount
        bankAccount={bankAccount}
        venuesNotLinkedLength={1}
        bankAccountsNumber={1}
      />
    )

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
      screen.getByRole('button', { name: 'Rattacher' })
    ).toBeInTheDocument()
  })

  it('should render without venues linked to bank account and with all venues linked to another account', () => {
    bankAccount.linkedVenues = []
    render(
      <ReimbursementBankAccount
        bankAccount={bankAccount}
        venuesNotLinkedLength={0}
        bankAccountsNumber={2}
      />
    )

    expect(
      screen.getByText(
        "Aucun lieu n'est rattaché à ce compte bancaire. Désélectionnez un lieu déjà rattaché et rattachez-le à ce compte bancaire."
      )
    ).toBeInTheDocument()
  })

  it('should render with one venue not linked to bank account', () => {
    render(
      <ReimbursementBankAccount
        bankAccount={bankAccount}
        venuesNotLinkedLength={1}
        bankAccountsNumber={2}
      />
    )

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
    render(
      <ReimbursementBankAccount
        bankAccount={bankAccount}
        venuesNotLinkedLength={2}
        bankAccountsNumber={1}
      />
    )

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
    render(
      <ReimbursementBankAccount
        bankAccount={bankAccount}
        venuesNotLinkedLength={2}
        bankAccountsNumber={1}
      />
    )

    expect(
      screen.getByText('Certains de vos lieux ne sont pas rattachés')
    ).toBeInTheDocument()
  })

  it('should display error icon if one or more venues are not linked to an account', () => {
    bankAccount.linkedVenues = []
    render(
      <ReimbursementBankAccount
        bankAccount={bankAccount}
        venuesNotLinkedLength={2}
        bankAccountsNumber={1}
      />
    )

    expect(
      screen.getByRole('img', { name: 'Une action est requise' })
    ).toBeInTheDocument()
  })

  it('should render with all venues linked to the account', () => {
    render(
      <ReimbursementBankAccount
        bankAccount={bankAccount}
        venuesNotLinkedLength={0}
        bankAccountsNumber={1}
      />
    )

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
})
