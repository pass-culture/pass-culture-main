import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { CollectiveOffersBookableCard } from './CollectiveOffersBookableCard'

describe.skip('<CollectiveOffersBookableCard />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<CollectiveOffersBookableCard offers={[]} />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
