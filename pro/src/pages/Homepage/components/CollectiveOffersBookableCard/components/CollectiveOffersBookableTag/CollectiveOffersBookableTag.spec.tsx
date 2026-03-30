import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { CollectiveOffersBookableTag } from './CollectiveOffersBookableTag'

describe('<CollectiveOffersBookableTag />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<CollectiveOffersBookableTag />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
