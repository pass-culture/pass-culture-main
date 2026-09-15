import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { SettlementRowInvoicesModal } from './SettlementRowInvoicesModal'

describe('<SettlementRowInvoiceModal />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<SettlementRowInvoicesModal />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
