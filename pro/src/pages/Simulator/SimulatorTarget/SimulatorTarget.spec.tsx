import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SimulatorTarget } from './SimulatorTarget'

describe('<SimulatorTarget />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<SimulatorTarget />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
