import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { WelcomeStepAdvantages } from '@/pages/WelcomeCarousel/WelcomeStepAdvantages/WelcomeStepAdvantages'

const mockNavigate = vi.fn()
vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useNavigate: () => mockNavigate,
    default: vi.fn(),
  }
})

const renderWelcomeStepAdvantages = () => {
  return renderWithProviders(<WelcomeStepAdvantages />)
}

describe('<WelcomeStepAdvantages />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWelcomeStepAdvantages()

    expect(await axe(container)).toHaveNoViolations()
  })
})
