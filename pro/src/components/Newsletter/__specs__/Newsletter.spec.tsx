import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Newsletter } from '../Newsletter'

const renderNewsletter = () => renderWithProviders(<Newsletter />)

describe('Newsletter', () => {
  it('should render review dialog when clicking on the review button', () => {
    renderNewsletter()
    const newsletterLink = screen.getByRole('link', {
      name: 'Inscrivez-vous à notre newsletter pour recevoir les actualités du pass Culture',
    })
    expect(newsletterLink).toHaveAttribute(
      'href',
      'https://04a7f3c7.sibforms.com/serve/MUIFAPpqRUKo_nexWvrSwpAXBv-P4ips11dOuqZz5d5FnAbtVD5frxeX6yLHjJcPwiiYAObkjhhcOVTlTkrd7XZDk6Mb2pbWTeaI-BUB6GK-G1xdra_mo-D4xAQsX5afUNHKIs3E279tzr9rDkHn3zVhIHZhcY14BiXhobwL6aFlah1-oXmy_RbznM0dtxVdaWHBPe2z0rYudrUw'
    )
  })
})
