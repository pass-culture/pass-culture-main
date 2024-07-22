import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { apiAdage } from 'apiClient/api'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  OfferFavoriteButton,
  OfferFavoriteButtonProps,
} from '../OfferFavoriteButton'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logFavOfferButtonClick: vi.fn(),
    deleteFavoriteForCollectiveOfferTemplate: vi.fn(),
    postCollectiveTemplateFavorites: vi.fn(),
  },
}))

const renderOfferFavoriteButton = (props: OfferFavoriteButtonProps) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <OfferFavoriteButton {...props} />
    </AdageUserContextProvider>
  )
}

describe('OfferFavoriteButton', () => {
  const defaultProps: OfferFavoriteButtonProps = {
    offer: defaultCollectiveTemplateOffer,
    queryId: 'ABC123',
  }

  it('should send event when offer is added to favorites', async () => {
    renderOfferFavoriteButton(defaultProps)

    await userEvent.click(
      screen.getByRole('button', { name: 'Mettre en favoris' })
    )
    expect(apiAdage.logFavOfferButtonClick).toHaveBeenCalledWith({
      offerId: defaultProps.offer.id,
      queryId: defaultProps.queryId,
      iframeFrom: '/',
      isFavorite: true,
    })
  })

  it('should send event when offer is remove from favorites', async () => {
    renderOfferFavoriteButton({
      ...defaultProps,
      offer: { ...defaultProps.offer, isFavorite: true },
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer des favoris' })
    )
    expect(apiAdage.logFavOfferButtonClick).toHaveBeenCalledWith({
      offerId: defaultProps.offer.id,
      queryId: defaultProps.queryId,
      iframeFrom: '/',
      isFavorite: false,
    })
  })
})
