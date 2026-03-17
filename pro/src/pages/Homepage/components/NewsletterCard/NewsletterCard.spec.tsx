import { render, screen } from '@testing-library/react'

import { NewsletterCard } from './NewsletterCard'

it('should render correctly', () => {
  render(<NewsletterCard />)

  expect(screen.getByText('Suivez notre actualité !')).toBeVisible()
  expect(
    screen.getByText(
      'Renseignez votre adresse mail pour recevoir les actualités du pass Culture.'
    )
  ).toBeVisible()
  expect(screen.getByText('S’abonner à la newsletter')).toBeVisible()
})

it('should render newsletter subscription link', () => {
  render(<NewsletterCard />)

  expect(
    screen.getByRole('link', { name: /S’abonner à la newsletter/ })
  ).toHaveAttribute(
    'href',
    `https://04a7f3c7.sibforms.com/serve/MUIFAPpqRUKo_nexWvrSwpAXBv-P4ips11dOuqZz5d5FnAbtVD5frxeX6yLHjJcPwiiYAObkjhhcOVTlTkrd7XZDk6Mb2pbWTeaI-BUB6GK-G1xdra_mo-D4xAQsX5afUNHKIs3E279tzr9rDkHn3zVhIHZhcY14BiXhobwL6aFlah1-oXmy_RbznM0dtxVdaWHBPe2z0rYudrUw`
  )
})
