import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SimulatorResults } from './SimulatorResults'

describe('<SimulatorResults />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<SimulatorResults />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
