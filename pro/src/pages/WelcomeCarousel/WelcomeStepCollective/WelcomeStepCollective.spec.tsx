import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { WelcomeCarouselEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as WelcomeStepCollective } from './WelcomeStepCollective'

const mockLogEvent = vi.fn()

describe('<WelcomeStepNextSteps />', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<WelcomeStepCollective />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should log CLICKED_SEE_COLLECTIVE_OFFERS event when clicking the example link', async () => {
    renderWithProviders(<WelcomeStepCollective />)

    const link = screen.getByRole('link', {
      name: /Exemple d’offres pour les groupes scolaires/,
    })
    await userEvent.click(link)

    expect(mockLogEvent).toHaveBeenCalledWith(
      WelcomeCarouselEvents.CLICKED_SEE_COLLECTIVE_OFFERS,
      {
        from: '/',
      }
    )
  })
})
