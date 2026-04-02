import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SimulatorActivity } from './SimulatorActivity'

describe('<SimulatorActivity />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<SimulatorActivity />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
