import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { SettlementsFilters } from './SettlementsFilters'

describe('<SettlementsFilters />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<SettlementsFilters />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
