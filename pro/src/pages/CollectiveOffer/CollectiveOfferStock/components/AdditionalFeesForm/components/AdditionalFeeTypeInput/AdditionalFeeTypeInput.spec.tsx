import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { AdditionalFeeTypeInput } from './AdditionalFeeTypeInput'

describe('<AdditionalFeeTypeInput />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<AdditionalFeeTypeInput />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
