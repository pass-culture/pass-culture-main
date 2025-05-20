import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { RadioButton } from './RadioButton'

describe('<RadioButton />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<RadioButton variant="DEFAULT" />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
