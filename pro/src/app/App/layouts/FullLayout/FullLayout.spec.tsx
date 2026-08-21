import { axe } from 'vitest-axe'

import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

describe('<FullLayout />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <FullLayout>Full Layout Content</FullLayout>
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
