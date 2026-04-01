import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SignupFunnelLayout } from './SignupFunnelLayout'

describe('<SignupFunnelLayout />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<SignupFunnelLayout />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
