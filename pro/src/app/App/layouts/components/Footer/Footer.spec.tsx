import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Footer } from './Footer'

describe('<Footer />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<Footer />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
