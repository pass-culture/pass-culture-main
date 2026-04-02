import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SimulatorSiret } from './SimulatorSiret'

describe('<SimulatorSiret />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<SimulatorSiret />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
