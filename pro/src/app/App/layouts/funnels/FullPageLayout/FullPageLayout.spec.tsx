import { axe } from 'vitest-axe'

import { FullPageLayout } from '@/app/App/layouts/funnels/FullPageLayout/FullPageLayout'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

describe('<FullPageLayout />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<FullPageLayout />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
