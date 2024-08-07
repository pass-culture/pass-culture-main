import { screen } from '@testing-library/react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { Newsletter } from '../Newsletter'

const renderNewsletter = () => renderWithProviders(<Newsletter />)

describe('Newsletter', () => {
  it('should render review dialog when clicking on the review button', () => {
    renderNewsletter()
    const newsletterLink = screen.getByText(
      'Inscrivez-vous à notre newsletter pour recevoir les actualités du pass Culture'
    )
    expect(newsletterLink).toHaveAttribute(
      'href',
      'https://0d5544dc.sibforms.com/serve/MUIEALeDGWdeK5Sx3mk95POo84LXw0wfRuL7M0YSLmEBQczDtyf9RchpzXzPpraWplBsNGz3nhwEpSpqOVUz_OeUCphS-ds635cE-vXDtQwLDc76VZ4GgUuqnsONKJ1FX6oBCslhYqgA6kB2vcv4_tNTLKesJvidy2o24roIqFRdfawXEOgz8LBQ1C9dlrDpO_Dz6E5L0IO_Gzs1'
    )
  })
})
