import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { HomepageEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { NewsletterCard } from './NewsletterCard'

const mockLogEvent = vi.fn()

it('should render correctly', () => {
  renderWithProviders(<NewsletterCard />)

  expect(screen.getByText('Suivez notre actualité !')).toBeVisible()
  expect(
    screen.getByText(
      'Renseignez votre adresse mail pour recevoir les actualités du pass Culture.'
    )
  ).toBeVisible()
  expect(screen.getByText('S’abonner à la newsletter')).toBeVisible()
})

it('should render newsletter subscription link', () => {
  renderWithProviders(<NewsletterCard />)

  expect(
    screen.getByRole('link', { name: /S’abonner à la newsletter/ })
  ).toHaveAttribute(
    'href',
    `https://04a7f3c7.sibforms.com/serve/MUIFAPpqRUKo_nexWvrSwpAXBv-P4ips11dOuqZz5d5FnAbtVD5frxeX6yLHjJcPwiiYAObkjhhcOVTlTkrd7XZDk6Mb2pbWTeaI-BUB6GK-G1xdra_mo-D4xAQsX5afUNHKIs3E279tzr9rDkHn3zVhIHZhcY14BiXhobwL6aFlah1-oXmy_RbznM0dtxVdaWHBPe2z0rYudrUw`
  )
})
it('should log CLICKED_NEWSLETTER on click', async () => {
  const user = userEvent.setup()

  vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
    logEvent: mockLogEvent,
  }))

  renderWithProviders(<NewsletterCard />)

  await user.click(
    screen.getByRole('link', { name: /S.abonner à la newsletter/ })
  )

  expect(mockLogEvent).toHaveBeenCalledWith(HomepageEvents.CLICKED_NEWSLETTER)
})
