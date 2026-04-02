import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Simulator } from './Simulator'

describe('<Simulator />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<Simulator />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
