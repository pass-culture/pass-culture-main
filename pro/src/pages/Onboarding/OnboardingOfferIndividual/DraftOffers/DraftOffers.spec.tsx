import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { DraftOffers } from './DraftOffers'

const renderDraftOffers = (options?: RenderWithProvidersOptions) => {
  return renderWithProviders(<DraftOffers offers={[]} />, { ...options })
}

vi.mock('@/apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
  },
}))

describe('<DraftOffers />', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
  })

  it('should render correctly', async () => {
    renderDraftOffers()

    expect(
      await screen.findByRole('heading', {
        name: 'Reprendre une offre déjà commencée',
      })
    ).toBeInTheDocument()
  })

  it('should not have accessibility violations', async () => {
    const { container } = renderDraftOffers()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(await axe(container)).toHaveNoViolations()
  })
})
