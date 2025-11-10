import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { Pagination } from './Pagination'

describe('<Pagination />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<Pagination />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
