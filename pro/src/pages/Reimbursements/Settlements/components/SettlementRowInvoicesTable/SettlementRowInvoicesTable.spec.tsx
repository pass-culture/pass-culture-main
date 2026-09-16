import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import type { InvoiceResponseV2Model } from '@/apiClient/v1'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SettlementRowInvoicesTable } from './SettlementRowInvoicesTable'

// Mock du composant InvoiceActions pour isoler le test de la table
vi.mock(
  '@/pages/Reimbursements/ReimbursementsInvoices/InvoiceTable/InvoiceActions',
  () => ({
    InvoiceActions: ({ invoice }: { invoice: InvoiceResponseV2Model }) => (
      <div data-testid="invoice-actions">{invoice.reference}</div>
    ),
  })
)

const BASE_INVOICES: InvoiceResponseV2Model[] = [
  {
    reference: 'INV-001',
    date: '2024-05-15T00:00:00Z',
    amount: 150.5,
  } as InvoiceResponseV2Model,
  {
    reference: 'INV-002',
    date: '2024-05-20T00:00:00Z',
    amount: -45.0,
  } as InvoiceResponseV2Model,
]

const renderTable = (
  invoices: InvoiceResponseV2Model[],
  isCaledonian = false
) => {
  return renderWithProviders(
    <SettlementRowInvoicesTable invoices={invoices} />,
    {
      storeOverrides: {
        user: {
          selectedAdminOfferer: {
            ...defaultGetOffererResponseModel,
            isCaledonian,
          },
        },
      },
    }
  )
}

describe('<SettlementRowInvoicesTable />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderTable(BASE_INVOICES)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render table headers and invoice data correctly in Euros', () => {
    renderTable(BASE_INVOICES)

    // Entêtes
    expect(screen.getByText('Référence')).toBeInTheDocument()
    expect(screen.getByText("Date d'émission")).toBeInTheDocument()
    expect(screen.getByText('Montant')).toBeInTheDocument()
    expect(screen.getByText('Actions')).toBeInTheDocument()

    // Lignes de données
    expect(screen.getAllByText('INV-001')).toHaveLength(2)
    expect(screen.getByText('15/05/2024')).toBeInTheDocument()
    expect(screen.getByText('+ 150,50 €')).toBeInTheDocument()

    expect(screen.getAllByText('INV-002')).toHaveLength(2)
    expect(screen.getByText('20/05/2024')).toBeInTheDocument()
    expect(screen.getByText('- 45,00 €')).toBeInTheDocument()

    expect(screen.getAllByTestId('invoice-actions')).toHaveLength(2)
  })

  it('should format amounts in Pacific Francs when offerer is Caledonian', () => {
    renderTable(BASE_INVOICES, true)

    expect(screen.getByText(/\+\s17\s960\sF/)).toBeInTheDocument()
    expect(screen.getByText(/-\s5\s370\sF/)).toBeInTheDocument()
  })

  it('should display empty state when invoices list is empty', () => {
    renderTable([])

    expect(
      screen.getByText('Pas de justificatifs pour ce virement')
    ).toBeInTheDocument()
  })
})
