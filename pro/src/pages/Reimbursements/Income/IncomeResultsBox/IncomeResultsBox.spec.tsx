import { render, screen } from '@testing-library/react'

import * as useIsCaledonian from '@/commons/hooks/useIsCaledonian'
import * as convertEuroToPacificFranc from '@/commons/utils/convertEuroToPacificFranc'

import { IncomeResultsBox } from './IncomeResultsBox'

describe('IncomeResultsBox', () => {
  beforeEach(() => {
    vi.spyOn(useIsCaledonian, 'useIsCaledonian').mockReturnValue(true)
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
      />
    )
    expect(screen.getByText('1234 F')).toBeInTheDocument()
  })
})
