import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { SettlementRowInvoicesTable } from './SettlementRowInvoicesTable'

describe('<SettlementRowInvoicesTable />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<SettlementRowInvoicesTable />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
