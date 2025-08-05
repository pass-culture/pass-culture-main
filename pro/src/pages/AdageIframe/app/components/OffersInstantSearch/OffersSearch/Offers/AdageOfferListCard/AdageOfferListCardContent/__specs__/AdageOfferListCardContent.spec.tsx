import { AuthenticatedResponse, EacFormat } from 'apiClient/adage'
import { screen } from '@testing-library/react'
import {
  defaultAdageUser,
  defaultCollectiveTemplateOffer,
} from 'commons/utils/factories/adageFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'

import {
  AdageOfferListCardContent,
  AdageOfferListCardContentProps,
} from '../AdageOfferListCardContent'

const renderAdageOfferListCardContent = (
  props: AdageOfferListCardContentProps = {
    offer: defaultCollectiveTemplateOffer,
  },
  adageUser: AuthenticatedResponse | null = defaultAdageUser
) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={adageUser}>
      <AdageOfferListCardContent {...props} />
    </AdageUserContextProvider>
  )
}

describe('AdageOfferListCardContent', () => {
  it('should show the offer formats if there are some', () => {
    renderAdageOfferListCardContent({
      offer: {
        ...defaultCollectiveTemplateOffer,
        formats: [EacFormat.CONCERT, EacFormat.CONF_RENCE_RENCONTRE],
      },
    })

    expect(screen.getByText('Concert'))
    expect(screen.getByText('Conférence, rencontre'))
  })

  it('should not show a list of formats if there is only one element', () => {
    renderAdageOfferListCardContent({
      offer: {
        ...defaultCollectiveTemplateOffer,
        formats: [EacFormat.CONCERT],
      },
    })

    expect(screen.queryByRole('list')).not.toBeInTheDocument()
  })
})
