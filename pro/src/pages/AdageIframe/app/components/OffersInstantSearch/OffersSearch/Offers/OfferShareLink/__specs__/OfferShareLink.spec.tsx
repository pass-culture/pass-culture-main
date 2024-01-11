import { screen } from '@testing-library/react'

import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferShareLink, { OfferShareLinkProps } from '../OfferShareLink'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logFavOfferButtonClick: vi.fn(),
    deleteFavoriteForCollectiveOfferTemplate: vi.fn(),
    postCollectiveTemplateFavorites: vi.fn(),
  },
}))

const renderOfferShareLink = (props: OfferShareLinkProps) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <OfferShareLink {...props} />
    </AdageUserContextProvider>
  )
}

describe('OfferShareLink', () => {
  const defaultProps: OfferShareLinkProps = {
    offer: { ...defaultCollectiveTemplateOffer, isTemplate: true },
  }

  it('should open email provider on click', () => {
    renderOfferShareLink(defaultProps)

    const shareLink = screen
      .getByRole('link', {
        name: /Partager l’offre par email/i,
      })
      .getAttribute('href')

    expect(shareLink).toContain('mailto')
  })
})
