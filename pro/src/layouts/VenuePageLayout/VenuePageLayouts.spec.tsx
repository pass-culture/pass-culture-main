import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { VenuePageLayout } from './VenuePageLayouts'

vi.mock('@/app/App/layouts/BasicLayout/BasicLayout', () => ({
  BasicLayout: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
}))

vi.mock('./components/Header', () => ({
  Header: ({ context }: { context: string }) => (
    <div data-testid="header">{context}</div>
  ),
}))

const renderVenuePageLayout = (path: string) =>
  renderWithProviders(<VenuePageLayout />, { initialRouterEntries: [path] })

describe('VenuePageLayout', () => {
  it('should render the partner page context by default', () => {
    renderVenuePageLayout('/partenaire/page-partenaire')

    expect(screen.getByText(/Page sur l/)).toBeInTheDocument()
    expect(screen.getByTestId('header')).toHaveTextContent('partnerPage')
  })

  it('should render the collective context on a collective page', () => {
    renderVenuePageLayout('/partenaire/page-collective')

    expect(screen.getByText('Page dans ADAGE')).toBeInTheDocument()
    expect(screen.getByTestId('header')).toHaveTextContent('collective')
  })
})
