import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { CollectiveOffersBookableCTA } from './CollectiveOffersBookableCTA'

describe('<CollectiveOffersBookableCTA />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<CollectiveOffersBookableCTA />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
