import { AlreadyHasAccount } from 'components/AlreadyHasAccount/AlreadyHasAccount'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

describe('<AlreadyHasAccount />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<AlreadyHasAccount />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
