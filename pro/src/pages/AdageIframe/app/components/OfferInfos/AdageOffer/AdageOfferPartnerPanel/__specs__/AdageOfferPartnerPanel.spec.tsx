import { screen } from '@testing-library/react'
import { describe } from 'vitest'

import {
  defaultAdageUser,
  defaultCollectiveTemplateOffer,
} from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import {
  AdageOfferPartnerPanel,
  type AdageOfferPartnerPanelProps,
} from '../AdageOfferPartnerPanel'

function renderAdageOfferPartnerPanel(
  props: AdageOfferPartnerPanelProps = {
    offer: defaultCollectiveTemplateOffer,
    adageUser: defaultAdageUser,
    isPreview: false,
  }
) {
  return renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
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
      adageUser: defaultAdageUser,
    })

    expect(
      screen.getByRole('link', {
        name: /Voir la page partenaire/,
      })
    ).toBeInTheDocument()
  })

  it('should not show the partner page link if the offer venue no adageId', () => {
    renderAdageOfferPartnerPanel({
      offer: {
        ...defaultCollectiveTemplateOffer,
        venue: { ...defaultCollectiveTemplateOffer.venue, adageId: undefined },
      },
      adageUser: defaultAdageUser,
    })

    expect(
      screen.queryByRole('link', {
        name: 'Nouvelle fenêtre Voir la page partenaire',
      })
    ).toBeFalsy()
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
      adageUser: defaultAdageUser,
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
      adageUser: defaultAdageUser,
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
      adageUser: defaultAdageUser,
    })

    expect(screen.getByText(/75000/)).toBeInTheDocument()
  })

  it('should show the partner distance to school', () => {
    renderAdageOfferPartnerPanel({
      offer: {
        ...defaultCollectiveTemplateOffer,
        venue: {
          ...defaultCollectiveTemplateOffer.venue,
          coordinates: { latitude: 1, longitude: 1 },
          city: undefined,
          postalCode: undefined,
        },
      },
      adageUser: { ...defaultAdageUser, lat: 2, lon: 2 },
    })

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

  it('should show a generic distance to school if the offer is a preview', () => {
    renderAdageOfferPartnerPanel({
      offer: defaultCollectiveTemplateOffer,
      isPreview: true,
    })

    expect(
      screen.getByText(/à X km de votre établissement scolaire/)
    ).toBeInTheDocument()
  })
})
