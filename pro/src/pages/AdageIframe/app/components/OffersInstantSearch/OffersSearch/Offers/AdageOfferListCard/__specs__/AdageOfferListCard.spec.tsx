import { screen } from '@testing-library/react'

import { AuthenticatedResponse } from 'apiClient/adage'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  AdageOfferListCard,
  AdageOfferListCardProps,
} from '../AdageOfferListCard'

const renderAdageOfferListCard = (
  props: AdageOfferListCardProps = {
    offer: defaultCollectiveTemplateOffer,
  },
  adageUser: AuthenticatedResponse | null = defaultAdageUser
) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={adageUser}>
      <AdageOfferListCard {...props} />
    </AdageUserContextProvider>
  )
}

describe('AdageOfferListCard', () => {
  it('should show the card with the offer title', () => {
    renderAdageOfferListCard()

    expect(
      screen.getByRole('heading', { name: defaultCollectiveTemplateOffer.name })
    )
  })

  it('should show the card image if it has one', () => {
    renderAdageOfferListCard({
      offer: { ...defaultCollectiveTemplateOffer, imageUrl: 'testUrl' },
    })

    expect(screen.getByRole('img')).toHaveAttribute('src', 'testUrl')
  })

  it('should show the favorite button if the offer is template and the user has the right to use favorites', () => {
    renderAdageOfferListCard()

    expect(
      screen.getByRole('button', { name: 'Mettre en favoris' })
    ).toBeInTheDocument()
  })

  it('should show the share link if the offer is template', () => {
    renderAdageOfferListCard()

    expect(
      screen.getByRole('link', { name: 'Partager par email' })
    ).toBeInTheDocument()
  })
})
