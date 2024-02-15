import { screen } from '@testing-library/react'

import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import AdageOfferPartnerPanel, {
  AdageOfferPartnerPanelProps,
} from '../AdageOfferPartnerPanel'

function renderAdageOfferPartnerPanel(
  props: AdageOfferPartnerPanelProps = {
    offer: defaultCollectiveTemplateOffer,
  },
  user = defaultAdageUser
) {
  return renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <AdageOfferPartnerPanel {...props} />
    </AdageUserContextProvider>
  )
}

describe('AdageOfferPartnerPanel', () => {
  it('should render the cultural partner panel', () => {
    renderAdageOfferPartnerPanel()

    expect(
      screen.getByRole('heading', { name: 'Partenaire culturel' })
    ).toBeInTheDocument()
  })

  it('should show the partner page link if the offer venue has an adageId', () => {
    renderAdageOfferPartnerPanel({
      offer: {
        ...defaultCollectiveTemplateOffer,
        venue: { ...defaultCollectiveTemplateOffer.venue, adageId: '123' },
      },
    })

    expect(
      screen.getByRole('link', {
        name: 'Nouvelle fenêtre Voir la page partenaire',
      })
    ).toBeInTheDocument()
  })

  it('should not show the partner page link if the offer venue no adageId', () => {
    renderAdageOfferPartnerPanel({
      offer: {
        ...defaultCollectiveTemplateOffer,
        venue: { ...defaultCollectiveTemplateOffer.venue, adageId: undefined },
      },
    })

    expect(
      screen.queryByRole('link', {
        name: 'Nouvelle fenêtre Voir la page partenaire',
      })
    ).not.toBeInTheDocument()
  })

  it('should show the partner city and postal code', () => {
    renderAdageOfferPartnerPanel({
      offer: {
        ...defaultCollectiveTemplateOffer,
        venue: {
          ...defaultCollectiveTemplateOffer.venue,
          city: 'Paris',
          postalCode: '75000',
        },
      },
    })

    expect(screen.getByText(/à Paris 75000/)).toBeInTheDocument()
  })

  it('should only show the partner city if there is no postal code', () => {
    renderAdageOfferPartnerPanel({
      offer: {
        ...defaultCollectiveTemplateOffer,
        venue: {
          ...defaultCollectiveTemplateOffer.venue,
          city: 'Paris',
          postalCode: undefined,
        },
      },
    })

    expect(screen.getByText(/à Paris/)).toBeInTheDocument()
  })

  it('should only show the partner postal code if there is no city', () => {
    renderAdageOfferPartnerPanel({
      offer: {
        ...defaultCollectiveTemplateOffer,
        venue: {
          ...defaultCollectiveTemplateOffer.venue,
          city: undefined,
          postalCode: '75000',
        },
      },
    })

    expect(screen.getByText(/75000/)).toBeInTheDocument()
  })

  it('should show the partner distance to school', () => {
    renderAdageOfferPartnerPanel(
      {
        offer: {
          ...defaultCollectiveTemplateOffer,
          venue: {
            ...defaultCollectiveTemplateOffer.venue,
            coordinates: { latitude: 1, longitude: 1 },
            city: undefined,
            postalCode: undefined,
          },
        },
      },
      { ...defaultAdageUser, lat: 2, lon: 2 }
    )

    expect(
      screen.getByText(/à 157 km de votre établissement scolaire/)
    ).toBeInTheDocument()
  })

  it('should show the cultural partner contact button', () => {
    renderAdageOfferPartnerPanel()

    expect(
      screen.getByRole('button', { name: 'Contacter le partenaire' })
    ).toBeInTheDocument()
  })
})
