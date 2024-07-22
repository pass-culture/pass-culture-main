import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import {
  BankAccountApplicationStatus,
  BankAccountResponseModel,
  ManagedVenues,
} from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import { ReimbursementBankAccount } from '../ReimbursementBankAccount'

const mockLogEvent = vi.fn()
const mockUpdateButtonClick = vi.fn()

const renderReimbursementBankAccount = (
  bankAccount: BankAccountResponseModel,
  managedVenues: ManagedVenues[],
  offererId = 0,
  hasWarning = false
) =>
  renderWithProviders(
    <Routes>
      <Route
        path="/remboursements/informations-bancaires"
        element={
          <ReimbursementBankAccount
            bankAccount={bankAccount}
            offererId={offererId}
            onUpdateButtonClick={mockUpdateButtonClick}
            managedVenues={managedVenues}
            hasWarning={hasWarning}
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
  let managedVenues: ManagedVenues[]

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

    managedVenues = [
      {
        bankAccountId: 1,
        commonName: 'venue',
        hasPricingPoint: false,
        id: 11,
      },
    ]
  })

  it('should render with pending bank account if status is in draft', () => {
    bankAccount.status = BankAccountApplicationStatus.EN_CONSTRUCTION
    renderReimbursementBankAccount(bankAccount, managedVenues)

    expect(screen.getByText('Bank account label')).toBeInTheDocument()
    expect(screen.getByText('IBAN : **** 0637')).toBeInTheDocument()
    expect(screen.getByText('BIC : BDFEFRPP')).toBeInTheDocument()

    expect(screen.getByText(/en cours de validation/)).toBeInTheDocument()
    expect(screen.getByText('Voir le dossier')).toBeInTheDocument()
    expect(
      screen.queryByText('Lieu(x) rattaché(s) à ce compte bancaire')
    ).not.toBeInTheDocument()
  })

  it('should render with pending bank account if status is WITH_PENDING_CORRECTIONS', () => {
    bankAccount.status = BankAccountApplicationStatus.A_CORRIGER
    renderReimbursementBankAccount(bankAccount, managedVenues)

    expect(screen.getByText('Bank account label')).toBeInTheDocument()
    expect(screen.getByText('IBAN : **** 0637')).toBeInTheDocument()
    expect(screen.getByText('BIC : BDFEFRPP')).toBeInTheDocument()

    expect(screen.getByText(/informations manquantes/)).toBeInTheDocument()
    expect(screen.getByText(/Compléter le dossier/)).toBeInTheDocument()
    expect(
      screen.queryByText('Lieu(x) rattaché(s) à ce compte bancaire')
    ).not.toBeInTheDocument()
  })

  it('should render with pending bank account if status is on going', () => {
    bankAccount.status = BankAccountApplicationStatus.EN_INSTRUCTION
    renderReimbursementBankAccount(bankAccount, managedVenues)

    expect(screen.getByText('Bank account label')).toBeInTheDocument()
    expect(screen.getByText('IBAN : **** 0637')).toBeInTheDocument()
    expect(screen.getByText('BIC : BDFEFRPP')).toBeInTheDocument()

    expect(screen.getByText(/en cours de validation/)).toBeInTheDocument()
    expect(screen.getByText('Voir le dossier')).toBeInTheDocument()
    expect(
      screen.queryByText('Lieu(x) rattaché(s) à ce compte bancaire')
    ).not.toBeInTheDocument()
  })

  it('should not render venues linked to bank account with only one bank account', () => {
    bankAccount.linkedVenues = []
    managedVenues.push({
      bankAccountId: null,
      commonName: 'second venue',
      hasPricingPoint: false,
      id: 12,
    })
    renderReimbursementBankAccount(bankAccount, managedVenues)

    expect(
      screen.queryByText(
        'Compte bancaire en cours de validation par nos services'
      )
    ).not.toBeInTheDocument()

    expect(
      screen.getByText('Lieu(x) rattaché(s) à ce compte bancaire')
    ).toBeInTheDocument()

    expect(
      screen.getByText('Aucun lieu n’est rattaché à ce compte bancaire.')
    ).toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: 'Rattacher un lieu' })
    ).toBeInTheDocument()
  })

  it('should render without venues linked to bank account and with all venues linked to another account', () => {
    bankAccount.linkedVenues = []
    renderReimbursementBankAccount(bankAccount, managedVenues, 2)

    expect(
      screen.getByText(
        'Aucun lieu n’est rattaché à ce compte bancaire. Désélectionnez un lieu déjà rattaché et rattachez-le à ce compte bancaire.'
      )
    ).toBeInTheDocument()
  })

  it('should render with several venues not linked to bank account', () => {
    managedVenues.push({
      bankAccountId: null,
      commonName: 'second venue',
      hasPricingPoint: false,
      id: 12,
    })
    renderReimbursementBankAccount(bankAccount, managedVenues)

    expect(
      screen.queryByText('Aucun lieu n’est rattaché à ce compte bancaire.')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText(
        'Aucun lieu n’est rattaché à ce compte bancaire. Désélectionnez un lieu déjà rattaché et rattachez-le à ce compte bancaire.'
      )
    ).not.toBeInTheDocument()

    expect(
      screen.getByText('Certains de vos lieux ne sont pas rattachés.')
    ).toBeInTheDocument()
    expect(screen.getByText('Le Petit Rintintin')).toBeInTheDocument()

    expect(screen.getByRole('button', { name: 'Modifier' })).toBeInTheDocument()
  })

  it('should render with several venues not linked to bank account', () => {
    managedVenues.push({
      bankAccountId: null,
      commonName: 'second venue',
      hasPricingPoint: false,
      id: 12,
    })
    renderReimbursementBankAccount(bankAccount, managedVenues)

    expect(
      screen.getByText('Certains de vos lieux ne sont pas rattachés.')
    ).toBeInTheDocument()
  })

  it('should display error icon if one or more venues are not linked to an account', () => {
    bankAccount.linkedVenues = []
    managedVenues.push({
      bankAccountId: 1,
      commonName: 'second venue',
      hasPricingPoint: false,
      id: 12,
    })
    renderReimbursementBankAccount(bankAccount, managedVenues, 1, true)

    expect(
      screen.getByRole('img', { name: 'Une action est requise' })
    ).toBeInTheDocument()
  })

  it('should not render error and warning messages when all venues are linked', () => {
    renderReimbursementBankAccount(bankAccount, managedVenues)

    expect(
      screen.queryByRole('img', { name: 'Une action est requise' })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText('Aucun lieu n’est rattaché à ce compte bancaire.')
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText(
        'Aucun lieu n’est rattaché à ce compte bancaire. Désélectionnez un lieu déjà rattaché et rattachez-le à ce compte bancaire.'
      )
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText('Certains de vos lieux ne sont pas rattachés.')
    ).not.toBeInTheDocument()
  })

  describe('trackers', () => {
    beforeEach(() => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
    })

    it('should track attach venue button click', async () => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))

      bankAccount.linkedVenues = []
      managedVenues[0]!.bankAccountId = null
      renderReimbursementBankAccount(bankAccount, managedVenues)

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

    it('should track attach venue button click', async () => {
      renderReimbursementBankAccount(bankAccount, managedVenues)

      await userEvent.click(screen.getByRole('button', { name: 'Modifier' }))
      expect(mockLogEvent).toHaveBeenCalledWith(
        BankAccountEvents.CLICKED_CHANGE_VENUE_TO_BANK_ACCOUNT,
        {
          from: '/remboursements/informations-bancaires',
          offererId: 0,
        }
      )
    })

    it('should track follow up bank account link click', async () => {
      renderReimbursementBankAccount(
        {
          ...bankAccount,
          status: BankAccountApplicationStatus.EN_CONSTRUCTION,
        },
        managedVenues
      )
      await userEvent.click(
        screen.getByRole('link', { name: 'Nouvelle fenêtre' })
      )
      expect(mockLogEvent).toHaveBeenCalledWith(
        BankAccountEvents.CLICKED_BANK_DETAILS_RECORD_FOLLOW_UP,
        {
          from: '/remboursements/informations-bancaires',
          offererId: 0,
        }
      )
    })
  })

  it('should call the onUpdateButtonClick function when clicking the action button', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    bankAccount.linkedVenues = []
    managedVenues[0]!.bankAccountId = null
    renderReimbursementBankAccount(bankAccount, managedVenues)

    await userEvent.click(
      screen.getByRole('button', { name: 'Rattacher un lieu' })
    )
    expect(mockUpdateButtonClick).toHaveBeenCalled()
  })

  it('should not display bank any wording or button under bank account card if offerer has no venue', () => {
    bankAccount.linkedVenues = []
    renderReimbursementBankAccount(bankAccount, [])

    expect(
      screen.getByText('Lieu(x) rattaché(s) à ce compte bancaire')
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: 'Rattacher un lieu' })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('img', { name: 'Une action est requise' })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText('Aucun lieu n’est rattaché à ce compte bancaire.')
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText(
        'Aucun lieu n’est rattaché à ce compte bancaire. Désélectionnez un lieu déjà rattaché et rattachez-le à ce compte bancaire.'
      )
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText('Certains de vos lieux ne sont pas rattachés.')
    ).not.toBeInTheDocument()
  })
})
