import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { HomepageEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { HomepageVariant } from '../types'
import {
  WEBINAR_LINKS,
  WebinarCard,
  type WebinarCardProps,
} from './WebinarCard'

const mockLogEvent = vi.fn()

const renderWebinarCard = (props: WebinarCardProps) => {
  return renderWithProviders(<WebinarCard {...props} />)
}

describe('WebinarCard', () => {
  it('should render the webinar card with the collective content', () => {
    renderWebinarCard({ variant: HomepageVariant.COLLECTIVE })

    expect(
      screen.getByRole('heading', {
        name: /Participer à nos webinaires sur la part collective !/i,
      })
    ).toBeVisible()

    expect(screen.getByRole('link')).toHaveAttribute(
      'href',
      WEBINAR_LINKS[HomepageVariant.COLLECTIVE]
    )
  })

  it('should render the webinar card with the individual content', () => {
    renderWebinarCard({ variant: HomepageVariant.INDIVIDUAL })

    expect(
      screen.getByRole('heading', {
        name: /Participer à nos webinaires sur la part individuelle !/i,
      })
    ).toBeVisible()

    expect(screen.getByRole('link')).toHaveAttribute(
      'href',
      WEBINAR_LINKS[HomepageVariant.INDIVIDUAL]
    )
  })

  it('should log CLICKED_WEBINAR on click', async () => {
    const user = userEvent.setup()

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderWebinarCard({ variant: HomepageVariant.INDIVIDUAL })

    await user.click(
      screen.getByRole('link', { name: /S’inscrire aux prochaines sessions/ })
    )

    expect(mockLogEvent).toHaveBeenCalledWith(HomepageEvents.CLICKED_WEBINAR, {
      variant: HomepageVariant.INDIVIDUAL,
    })
  })
})
