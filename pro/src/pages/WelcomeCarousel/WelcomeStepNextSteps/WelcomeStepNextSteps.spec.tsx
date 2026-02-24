import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { WelcomeCarouselEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as WelcomeStepNextSteps } from './WelcomeStepNextSteps'

const mockLogEvent = vi.fn()

describe('<WelcomeStepNextSteps />', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<WelcomeStepNextSteps />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should log CLICKED_SEE_WEBINAR event when clicking the webinar link', async () => {
    renderWithProviders(<WelcomeStepNextSteps />)

    const webinarLink = screen.getByRole('link', {
      name: /Participez à notre prochain webinaire/,
    })
    await userEvent.click(webinarLink)

    expect(mockLogEvent).toHaveBeenCalledWith(
      WelcomeCarouselEvents.CLICKED_SEE_WEBINAR,
      {
        from: '/',
      }
    )
  })
})
