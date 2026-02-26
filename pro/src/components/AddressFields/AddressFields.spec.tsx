import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { AddressFields } from './AddressFields'

describe('<AddressFields />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<AddressFields />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
