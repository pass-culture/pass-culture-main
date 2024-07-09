import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import {
  BankAccountApplicationStatus,
  BankAccountResponseModel,
  InvoiceResponseV2Model,
} from 'apiClient/v1'
import { ReimbursementsContextProps } from 'pages/Reimbursements/Reimbursements'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { ReimbursementsDetails } from '../ReimbursementsDetails/ReimbursementsDetails'

vi.mock('utils/date', async () => ({
  ...(await vi.importActual('utils/date')),
  getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
}))

const contextData: ReimbursementsContextProps = {
  selectedOfferer: defaultGetOffererResponseModel,
  setSelectedOfferer: function () {},
}
vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useOutletContext: () => contextData,
}))

const bankAccountId = 12
const BANK_ACCOUNTS: BankAccountResponseModel[] = [
  {
    id: bankAccountId,
    label: 'Bank account 1',
    bic: '',
    dateCreated: '',
    isActive: false,
    linkedVenues: [],
    obfuscatedIban: '',
    status: BankAccountApplicationStatus.ACCEPTE,
  },
  {
    id: 13,
    label: 'Bank account 2',
    bic: '',
    dateCreated: '',
    isActive: false,
    linkedVenues: [],
    obfuscatedIban: '',
    status: BankAccountApplicationStatus.ACCEPTE,
  },
]

const BASE_INVOICES: InvoiceResponseV2Model[] = [
  {
    date: '13-01-2022',
    reference: 'ABC',
    amount: 100,
    url: 'url1',
    cashflowLabels: [],
  },
  {
    date: '13-01-2022',
    reference: 'DEF',
    amount: 100,
    url: 'url2',
    cashflowLabels: [],
  },
]

const renderReimbursementsDetails = (options?: RenderWithProvidersOptions) => {
  renderWithProviders(<ReimbursementsDetails />, {
    user: sharedCurrentUserFactory(),
    ...options,
  })
}

describe('reimbursementsWithFilters', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      bankAccounts: BANK_ACCOUNTS,
      id: defaultGetOffererResponseModel.id,
      managedVenues: [],
    })
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)
  })

  it('should display the reimbursement details callout message', async () => {
    renderReimbursementsDetails()

    expect(
      await screen.findByText(
        /Nouveau ! Les détails de remboursements seront bientôt téléchargeables depuis l’onglet justificatif./
      )
    ).toBeInTheDocument()
  })

  it('should not disable buttons when the period dates are filled', async () => {
    renderReimbursementsDetails()

    expect(
      await screen.findByRole('button', {
        name: /Télécharger/i,
      })
    ).toBeEnabled()
    expect(
      screen.getByRole('link', { name: 'Nouvelle fenêtre Afficher' })
    ).toBeInTheDocument()
  })

  it('should disable buttons if user is admin and no bank account filter is selected', async () => {
    renderReimbursementsDetails({
      user: sharedCurrentUserFactory({ isAdmin: true }),
    })

    expect(
      await screen.findByRole('button', {
        name: /Télécharger/i,
      })
    ).toBeDisabled()
    expect(
      screen.getByRole('link', {
        name: 'Nouvelle fenêtre Afficher Action non disponible',
      })
    ).toBeInTheDocument()
  })

  it('should enable buttons when admin user selects a bank account', async () => {
    renderReimbursementsDetails({
      user: sharedCurrentUserFactory({ isAdmin: true }),
    })

    await userEvent.selectOptions(
      await screen.findByLabelText('Compte bancaire'),
      'Bank account 1'
    )

    expect(
      screen.getByRole('button', {
        name: /Télécharger/i,
      })
    ).toBeEnabled()
    expect(screen.getByRole('link', { name: /Afficher/ })).toHaveAttribute(
      'href',
      `/remboursements-details?offererId=${contextData.selectedOfferer!.id}&reimbursementPeriodBeginningDate=2020-11-15&reimbursementPeriodEndingDate=2020-12-15&bankAccountId=${bankAccountId}`
    )
  })

  it('should reset filters values', async () => {
    renderReimbursementsDetails()

    const startFilter = await screen.findByLabelText('Début de la période')
    const endFilter = screen.getByLabelText('Fin de la période')

    await userEvent.type(startFilter, '1998-11-12')
    await userEvent.type(endFilter, '1999-12-12')
    await userEvent.selectOptions(
      await screen.findByLabelText('Compte bancaire'),
      'Bank account 1'
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: /Réinitialiser les filtres/i,
      })
    )

    expect(screen.getByLabelText('Compte bancaire')).toHaveValue(
      'allBankAccounts'
    )
    expect(screen.getByLabelText('Début de la période')).toHaveValue(
      '2020-11-15'
    )
    expect(screen.getByLabelText('Fin de la période')).toHaveValue('2020-12-15')
  })

  it('should order bank accounts option by alphabetical order', async () => {
    renderReimbursementsDetails()

    const options = await within(
      await screen.findByLabelText('Compte bancaire')
    ).findAllByRole('option')

    expect(options[0].textContent).toBe('Tous les comptes bancaires')
    expect(options[1].textContent).toStrictEqual('Bank account 1')
    expect(options[2].textContent).toStrictEqual('Bank account 2')
    expect(api.getOffererBankAccountsAndAttachedVenues).toHaveBeenCalledTimes(1)
  })

  it('should update display button url when changing any filter', async () => {
    renderReimbursementsDetails()

    await userEvent.selectOptions(
      await screen.findByLabelText('Compte bancaire'),
      'Bank account 1'
    )

    const startInput = screen.getByLabelText('Début de la période')
    const endInput = screen.getByLabelText('Fin de la période')
    await userEvent.clear(startInput)
    await userEvent.clear(endInput)
    await userEvent.type(startInput, '1998-11-12')
    await userEvent.type(endInput, '1999-12-12')

    expect(screen.getByText(/Afficher/)).toHaveAttribute(
      'href',
      `/remboursements-details?offererId=${contextData.selectedOfferer!.id}&reimbursementPeriodBeginningDate=1998-11-12&reimbursementPeriodEndingDate=1999-12-12&bankAccountId=${bankAccountId}`
    )
  })

  it('should display no refunds message when user has no associated bank accounts', async () => {
    vi.spyOn(
      api,
      'getOffererBankAccountsAndAttachedVenues'
    ).mockResolvedValueOnce({ bankAccounts: [], id: 1, managedVenues: [] })
    renderReimbursementsDetails()

    expect(
      await screen.findByText('Aucun remboursement à afficher')
    ).toBeInTheDocument()
  })
})
