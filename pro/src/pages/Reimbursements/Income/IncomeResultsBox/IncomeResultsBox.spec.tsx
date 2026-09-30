import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import * as convertEuroToPacificFranc from '@/commons/utils/convertEuroToPacificFranc'

import { IncomeResultsBox } from './IncomeResultsBox'

describe('IncomeResultsBox', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <IncomeResultsBox
        type="revenue"
        income={{ individual: 100, collective: 0, total: 100 }}
        isCaledonian={true}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display total in CFP when isCaledonian is true (individual)', () => {
    vi.spyOn(
      convertEuroToPacificFranc,
      'convertEuroToPacificFranc'
    ).mockImplementation(() => 1234)
    render(
      <IncomeResultsBox
        type="revenue"
        income={{ individual: 100, collective: 0, total: 100 }}
        isCaledonian={true}
      />
    )
    expect(screen.getByText('1 234 F')).toBeInTheDocument()
  })
})
