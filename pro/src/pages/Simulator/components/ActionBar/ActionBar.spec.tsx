import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { ActionBar } from './ActionBar'

describe('<ActionBar />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<ActionBar />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
