import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { WelcomeCarousel } from './WelcomeCarousel'

const renderWelcomeCarroussel = (initialPath: string = '/bienvenue') => {
  return renderWithProviders(<WelcomeCarousel />, {
    initialRouterEntries: [initialPath],
  })
}
describe('<WelcomeCarousel />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWelcomeCarroussel()

    expect(await axe(container)).toHaveNoViolations()
  })
})
