import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import type { InvoiceResponseV2Model } from '@/apiClient/v1'

import type { ExtendedSettlementResponseModel } from '../SettlementTable/SettlementTable'
import { SettlementRowInvoicesModal } from './SettlementRowInvoicesModal'

vi.mock(
  '@/pages/Reimbursements/ReimbursementsInvoices/InvoiceTable/InvoiceActions',
  () => ({
    InvoiceActionVariant: { BUTTONS: 'BUTTONS' },
    InvoiceActions: ({ invoice }: { invoice: InvoiceResponseV2Model }) => (
      <button type="button">{`Télécharger ${invoice.reference}`}</button>
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
    expect(screen.getByText('2 justificatifs - 250,00 €')).toBeInTheDocument()

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
  })

  it('should render singular description when invoicesCount is 1', () => {
    const singleInvoiceRow = {
      ...BASE_SETTLEMENT_ROW,
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

    expect(screen.getByText('1 justificatif - 250,00 €')).toBeInTheDocument()
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

    expect(screen.getByText(/2 justificatifs - 29\s835\sF/)).toBeInTheDocument()
    expect(screen.getByText(/\+\s23\s865\sF/)).toBeInTheDocument()
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
