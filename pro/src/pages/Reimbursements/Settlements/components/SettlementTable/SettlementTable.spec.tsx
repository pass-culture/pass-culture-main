import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import type { ComponentProps } from 'react'
import { axe } from 'vitest-axe'

import {
  InvoiceStatus,
  SettlementDisplayedStatus,
  type SettlementResponseModel,
} from '@/apiClient/v1'
import * as useMediaQueryModule from '@/commons/hooks/useMediaQuery'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { noop } from '@/commons/utils/noop'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SettlementTable } from './SettlementTable'

vi.mock('../SettlementRowInvoicesTable/SettlementRowInvoicesTable', () => ({
  SettlementRowInvoicesTable: ({ invoices }: { invoices: unknown[] }) => (
    <div data-testid="invoices-table">Invoices count: {invoices.length}</div>
  ),
}))

vi.mock('../SettlementRowInvoicesModal/SettlementRowInvoicesModal', () => ({
  SettlementRowInvoicesModal: ({
    isOpen,
    onClose,
    settlementRow,
  }: {
    isOpen: boolean
    onClose: () => void
    settlementRow: SettlementResponseModel | null
  }) =>
    isOpen ? (
      <div data-testid="invoices-modal">
        <p>Modal content: {settlementRow?.label}</p>
        <button type="button" onClick={onClose}>
          Fermer la modale
        </button>
      </div>
    ) : null,
}))

vi.mock(
  '@/pages/Reimbursements/ReimbursementsInvoices/InvoiceTable/InvoiceDownloadActionsBar',
  () => ({
    InvoiceDownloadActionsBar: ({
      invoiceReferences,
      description,
    }: {
      invoiceReferences: string[]
      description?: string
    }) =>
      invoiceReferences.length > 0 ? (
        <div data-testid="download-actions-bar">
          <p>{description}</p>
          <p>Invoices count: {invoiceReferences.length}</p>
        </div>
      ) : null,
  })
)

const baseSettlement = {
  id: 1,
  label: 'VIR001',
  date: '2024-06-01',
  bankAccount: 'Compte principal',
  status: SettlementDisplayedStatus.EXECUTED,
  amount: 150,
  invoices: [
    {
      reference: 'J123456789',
      date: '2024-06-01',
      amount: 100,
      url: 'J123456789.invoice',
      status: InvoiceStatus.PAID,
    },
    {
      reference: 'J666666666',
      date: '2024-06-01',
      amount: -50,
      url: 'J666666666.invoice',
      status: InvoiceStatus.PAID,
    },
    {
      reference: 'J987654321',
      date: '2024-06-01',
      amount: 100,
      url: 'J987654321.invoice',
      status: InvoiceStatus.PAID,
    },
  ],
  resolvedBy: [],
} as SettlementResponseModel

const renderSettlementTable = (
  props: Partial<ComponentProps<typeof SettlementTable>> = {},
  offererOverrides: Partial<typeof defaultGetOffererResponseModel> = {}
) =>
  renderWithProviders(
    <SettlementTable
      settlements={[baseSettlement]}
      isLoading={false}
      hasSettlement={true}
      hasBankAccount={true}
      onFilterReset={noop}
      {...props}
    />,
    {
      storeOverrides: {
        user: {
          selectedAdminOfferer: {
            ...defaultGetOffererResponseModel,
            ...offererOverrides,
          },
        },
      },
    }
  )

describe('<SettlementTable />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderSettlementTable()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the settlement row with formatted data', () => {
    renderSettlementTable()

    expect(screen.getByRole('cell', { name: 'VIR001' })).toBeVisible()
    expect(screen.getByRole('cell', { name: '01/06/2024' })).toBeVisible()
    expect(screen.getByRole('cell', { name: 'Compte principal' })).toBeVisible()
    expect(screen.getByRole('cell', { name: '3' })).toBeVisible()
    expect(screen.getByRole('cell', { name: 'Virement émis' })).toBeVisible()
    expect(screen.getByRole('cell', { name: /^150,00\s€$/ })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Voir plus' })).toBeVisible()
    const tooltips = screen.getAllByRole('tooltip', { hidden: true })
    expect(tooltips).toHaveLength(2)
    expect(tooltips[0]).toHaveTextContent('Tout sélectionner')
    expect(tooltips[1]).toHaveTextContent('Compte principal')
  })

  it('renders the rejected settlement differently', () => {
    renderSettlementTable({
      settlements: [
        {
          ...baseSettlement,
          status: SettlementDisplayedStatus.REJECTED_UNRESOLVED,
        },
      ] as never,
    })

    expect(screen.queryByRole('cell', { name: '3' })).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Voir plus' })
    ).not.toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Remplacer le compte' })
    ).toBeVisible()
  })

  it('renders the rejected processed settlement differently', () => {
    renderSettlementTable({
      settlements: [
        {
          ...baseSettlement,
          status: SettlementDisplayedStatus.REJECTED_PROCESSED,
        },
      ] as never,
    })

    expect(screen.queryByRole('cell', { name: '3' })).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Voir plus' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('cell', { name: 'En attente de réémission' })
    ).toBeVisible()
  })

  it('renders the rejected solved settlement differently', () => {
    renderSettlementTable({
      settlements: [
        {
          ...baseSettlement,
          status: SettlementDisplayedStatus.REJECTED_SOLVED,
          resolvedBy: ['VIR1', 'VIR2'],
        },
      ] as never,
    })

    expect(screen.queryByRole('cell', { name: '3' })).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Voir plus' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('cell', { name: 'Voir VIR1, VIR2' })
    ).toBeVisible()
  })

  it('displays a dash when the settlement has no date', () => {
    renderSettlementTable({
      settlements: [{ ...baseSettlement, date: null }] as never,
    })

    expect(screen.getByText('-')).toBeVisible()
  })

  it('formats the amount in pacific francs for a Caledonian offerer', () => {
    renderSettlementTable({}, { isCaledonian: true })

    expect(screen.getByText('17 900 F')).toBeVisible()
  })

  it('shows the missing bank account empty state when hasBankAccount is false', () => {
    renderSettlementTable({
      hasBankAccount: false,
      hasSettlement: false,
      settlements: [],
    })

    expect(screen.getByText('Aucun compte bancaire rattaché')).toBeVisible()
    expect(
      screen.getByRole('link', { name: 'Rattacher un compte bancaire' })
    ).toHaveAttribute(
      'href',
      '/administration/remboursements/informations-bancaires'
    )
  })

  it('shows the no-settlement-yet empty state when hasSettlement is false but a bank account exists', () => {
    renderSettlementTable({ hasSettlement: false, settlements: [] })

    expect(screen.getByText('Aucun virement pour le moment')).toBeVisible()
    expect(
      screen.getByRole('link', { name: 'Voir mes justificatifs' })
    ).toHaveAttribute('href', '/administration/remboursements/justificatifs')
  })

  it('does not show an empty state when there is at least one settlement and a bank account', () => {
    renderSettlementTable()

    expect(
      screen.queryByText('Aucun virement pour le moment')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Aucun compte bancaire rattaché')
    ).not.toBeInTheDocument()
  })

  it('toggles the embedded invoices table when clicking "Voir plus" on desktop', async () => {
    const user = userEvent.setup()
    vi.spyOn(useMediaQueryModule, 'useMediaQuery').mockReturnValue(false)

    renderSettlementTable()

    expect(screen.queryByTestId('invoices-table')).not.toBeInTheDocument()

    const seeMoreButton = screen.getByRole('button', { name: 'Voir plus' })
    await user.click(seeMoreButton)

    expect(screen.getByTestId('invoices-table')).toBeInTheDocument()
    expect(screen.getByText('Invoices count: 3')).toBeInTheDocument()

    // Un second clic doit refermer la ligne affichée
    await user.click(seeMoreButton)
    expect(screen.queryByTestId('invoices-table')).not.toBeInTheDocument()
  })

  it('opens the invoices modal when clicking "Voir plus" on mobile/tablet viewport', async () => {
    const user = userEvent.setup()
    vi.spyOn(useMediaQueryModule, 'useMediaQuery').mockReturnValue(true)

    renderSettlementTable()

    expect(screen.queryByTestId('invoices-modal')).not.toBeInTheDocument()

    const seeMoreButton = screen.getByRole('button', { name: 'Voir plus' })
    await user.click(seeMoreButton)

    expect(screen.getByTestId('invoices-modal')).toBeInTheDocument()
    expect(screen.getByText('Modal content: VIR001')).toBeInTheDocument()

    // Fermeture de la modale via le bouton de fermeture
    const closeButton = screen.getByRole('button', { name: 'Fermer la modale' })
    await user.click(closeButton)

    expect(screen.queryByTestId('invoices-modal')).not.toBeInTheDocument()
  })
  it('should handle row selection and display InvoiceDownloadActionsBar with correct count and references', async () => {
    const user = userEvent.setup()
    renderSettlementTable({
      settlements: [
        baseSettlement,
        {
          ...baseSettlement,
          id: 2,
          label: 'VIR002',
          invoices: [
            {
              reference: 'J000000000',
              date: '2024-06-02',
              amount: 200,
              url: 'J000000000.invoice',
              status: InvoiceStatus.PAID,
            },
          ],
        },
      ] as never,
    })

    expect(screen.queryByTestId('download-actions-bar')).not.toBeInTheDocument()

    // Sélection du premier virement (contient 3 justificatifs)
    const checkboxes = screen.getAllByRole('checkbox')
    await user.click(checkboxes[1])

    expect(screen.getByTestId('download-actions-bar')).toBeInTheDocument()
    expect(screen.getByText('1 virement sélectionné')).toBeInTheDocument()
    expect(screen.getByText('Invoices count: 3')).toBeInTheDocument()

    // Sélection du second virement (ajoute 1 justificatif -> total 4)
    await user.click(checkboxes[2])

    expect(screen.getByText('2 virements sélectionnés')).toBeInTheDocument()
    expect(screen.getByText('Invoices count: 4')).toBeInTheDocument()
  })

  it('should disable selection checkbox for non-executed settlements or settlements without invoices', () => {
    renderSettlementTable({
      settlements: [
        {
          ...baseSettlement,
          id: 2,
          label: 'VIR_REJECTED',
          status: SettlementDisplayedStatus.REJECTED_UNRESOLVED,
        },
        {
          ...baseSettlement,
          id: 3,
          label: 'VIR_EMPTY',
          invoices: [],
        },
      ] as never,
    })

    const checkboxes = screen.getAllByRole('checkbox')
    expect(checkboxes[1]).toBeDisabled()
    expect(checkboxes[2]).toBeDisabled()
  })
})
