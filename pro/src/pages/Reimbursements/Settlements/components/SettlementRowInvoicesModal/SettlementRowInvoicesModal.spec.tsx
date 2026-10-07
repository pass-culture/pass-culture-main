import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import type { InvoiceResponseV2Model } from '@/apiClient/v1'

import type { ExtendedSettlementResponseModel } from '../SettlementTable/SettlementTable'
import { SettlementRowInvoicesModal } from './SettlementRowInvoicesModal'

vi.mock(
  '@/pages/Reimbursements/ReimbursementsInvoices/InvoiceTable/InvoiceActions',
  () => ({
    InvoiceActions: ({
      invoice,
      portalContainer,
    }: {
      invoice: InvoiceResponseV2Model
      portalContainer?: HTMLElement | null
    }) => (
      <button type="button" data-portal-container={portalContainer?.tagName}>
        {`Télécharger ${invoice.reference}`}
      </button>
    ),
  })
)

const BASE_SETTLEMENT_ROW: ExtendedSettlementResponseModel = {
  id: 1,
  label: 'VIR-001',
  amount: 250.0,
  invoicesCount: 2,
  isCaledonian: false,
  invoices: [
    {
      reference: 'INV-101',
      date: '2024-06-01T00:00:00Z',
      amount: 200.0,
    } as InvoiceResponseV2Model,
    {
      reference: 'INV-102',
      date: '2024-06-02T00:00:00Z',
      amount: 50.0,
    } as InvoiceResponseV2Model,
  ],
} as unknown as ExtendedSettlementResponseModel

describe('<SettlementRowInvoicesModal />', () => {
  it('should render nothing when settlementRow is null', () => {
    const { container } = render(
      <SettlementRowInvoicesModal
        isOpen={true}
        onClose={vi.fn()}
        settlementRow={null}
      />
    )

    expect(container).toBeEmptyDOMElement()
  })

  it('should render without accessibility violations when open', async () => {
    const { container } = render(
      <SettlementRowInvoicesModal
        isOpen={true}
        onClose={vi.fn()}
        settlementRow={BASE_SETTLEMENT_ROW}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render modal content correctly in Euros', () => {
    render(
      <SettlementRowInvoicesModal
        isOpen={true}
        onClose={vi.fn()}
        settlementRow={BASE_SETTLEMENT_ROW}
      />
    )

    // Titre et description (pluriel)
    expect(screen.getByText('VIR-001')).toBeInTheDocument()
    expect(screen.getByText('2 justificatifs')).toBeInTheDocument()
    expect(screen.getByText('250,00 €')).toBeInTheDocument()

    // Liste des justificatifs
    expect(screen.getByText('INV-101')).toBeInTheDocument()
    expect(screen.getByText('01/06/2024')).toBeInTheDocument()
    expect(screen.getByText('+ 200,00 €')).toBeInTheDocument()

    expect(screen.getByText('INV-102')).toBeInTheDocument()
    expect(screen.getByText('02/06/2024')).toBeInTheDocument()
    expect(screen.getByText('+ 50,00 €')).toBeInTheDocument()

    // Actions
    expect(
      screen.getByRole('button', { name: 'Télécharger INV-101' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Télécharger INV-101' })
    ).toHaveAttribute('data-portal-container', 'DIALOG')
  })

  it('should render singular description when invoicesCount is 1', () => {
    const singleInvoiceRow = {
      ...BASE_SETTLEMENT_ROW,
      amount: BASE_SETTLEMENT_ROW.invoices[0].amount,
      invoicesCount: 1,
      invoices: [BASE_SETTLEMENT_ROW.invoices[0]],
    }

    render(
      <SettlementRowInvoicesModal
        isOpen={true}
        onClose={vi.fn()}
        settlementRow={singleInvoiceRow}
      />
    )

    expect(screen.getByText('1 justificatif')).toBeInTheDocument()
    expect(screen.getByText('200,00 €')).toBeInTheDocument() // settlement
    expect(screen.getByText('+ 200,00 €')).toBeInTheDocument() // invoice
  })

  it('should render correctly when the settlement is a debit note', () => {
    const singleInvoiceRow = {
      ...BASE_SETTLEMENT_ROW,
      amount: -250.0,
      invoicesCount: 1,
      invoices: [{ ...BASE_SETTLEMENT_ROW.invoices[0], amount: -250.0 }],
    }

    render(
      <SettlementRowInvoicesModal
        isOpen={true}
        onClose={vi.fn()}
        settlementRow={singleInvoiceRow}
      />
    )

    expect(screen.getByText('1 justificatif')).toBeInTheDocument()
    expect(screen.getAllByText('- 250,00 €')).toHaveLength(2) // one for settlement, one for invoice
  })

  it('should format amounts in Pacific Francs when isCaledonian is true', () => {
    const caledonianRow = {
      ...BASE_SETTLEMENT_ROW,
      isCaledonian: true,
    }

    render(
      <SettlementRowInvoicesModal
        isOpen={true}
        onClose={vi.fn()}
        settlementRow={caledonianRow}
      />
    )

    expect(screen.getByText('2 justificatifs')).toBeInTheDocument()
    expect(screen.getByText('29 835 F')).toBeInTheDocument()
    expect(screen.getByText('+ 23 865 F')).toBeInTheDocument()
  })

  it('should call onClose when close button is clicked', async () => {
    const user = userEvent.setup()
    const handleClose = vi.fn()

    render(
      <SettlementRowInvoicesModal
        isOpen={true}
        onClose={handleClose}
        settlementRow={BASE_SETTLEMENT_ROW}
      />
    )

    const closeButton = screen.getByRole('button', { name: /fermer/i })
    await user.click(closeButton)

    expect(handleClose).toHaveBeenCalledTimes(1)
  })
})
