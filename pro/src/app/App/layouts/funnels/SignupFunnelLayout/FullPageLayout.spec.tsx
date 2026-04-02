import { FullPageLayout } from 'app/App/layouts/funnels/SignupFunnelLayout/FullPageLayout'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

describe('<FullPageLayout />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<FullPageLayout />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
