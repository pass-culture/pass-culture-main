import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { WelcomeCarouselEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as WelcomeStepIndividual } from './WelcomeStepIndividual'

const mockLogEvent = vi.fn()

describe('<WelcomeStepNextSteps />', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<WelcomeStepIndividual />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should log CLICKED_SEE_INDIV_OFFERS event when clicking the example link', async () => {
    renderWithProviders(<WelcomeStepIndividual />)

    const link = screen.getByRole('link', {
      name: /Exemples d'offres pour les jeunes/,
    })
    await userEvent.click(link)

    expect(mockLogEvent).toHaveBeenCalledWith(
      WelcomeCarouselEvents.CLICKED_SEE_INDIV_OFFERS,
      {
        from: '/',
      }
    )
  })
})
