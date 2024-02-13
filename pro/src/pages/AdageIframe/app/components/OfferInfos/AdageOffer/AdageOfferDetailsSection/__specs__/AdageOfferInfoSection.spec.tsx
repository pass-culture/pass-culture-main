import { render, screen } from '@testing-library/react'

import { OfferAddressType } from 'apiClient/adage'
import { defaultCollectiveTemplateOffer } from 'utils/adageFactories'

import AdageOfferInfoSection, {
  AdageOfferInfoSectionProps,
} from '../AdageOfferInfoSection'

function renderAdageOfferInfoSection(
  props: AdageOfferInfoSectionProps = {
    offer: defaultCollectiveTemplateOffer,
  }
) {
  return render(<AdageOfferInfoSection {...props} />)
}

describe('AdageOfferInfoSection', () => {
  it('should show the offer location for an offer at a specific address', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        offerVenue: {
          addressType: OfferAddressType.OTHER,
          otherAddress: 'offer address test',
        },
      },
    })

    expect(screen.getByText('offer address test')).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Lieu où se déroulera l’offre' })
    ).toBeInTheDocument()
  })

  it('should show the offer location for an offer at the school', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        offerVenue: {
          ...defaultCollectiveTemplateOffer.offerVenue,
          addressType: OfferAddressType.SCHOOL,
        },
      },
    })

    expect(
      screen.getByText(
        'Le partenaire culturel se déplace dans les établissements scolaires.'
      )
    ).toBeInTheDocument()
  })

  it('should show the offer location for an offer at the offerer venue', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        offerVenue: {
          ...defaultCollectiveTemplateOffer.offerVenue,
          addressType: OfferAddressType.OFFERER_VENUE,
          address: 'test venue address',
        },
      },
    })

    expect(screen.getByText(/test venue address/)).toBeInTheDocument()
  })

  it('should show the dates of a template offer that has specific dates', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        dates: {
          end: '2024-01-29T23:00:28.040559Z',
          start: '2024-01-23T23:00:28.040547Z',
        },
      },
    })

    expect(
      screen.getByText('Du 23 janvier au 29 janvier 2024 à 23h')
    ).toBeInTheDocument()
  })

  it('should show that the offer is permanent if it has no dates', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        dates: undefined,
      },
    })

    expect(
      screen.getByText(
        'Tout au long de l’année scolaire (l’offre est permanente)'
      )
    ).toBeInTheDocument()
  })

  it('should display the offer price details', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        educationalPriceDetail: 'The detail of the price',
      },
    })

    expect(
      screen.getByRole('heading', { name: 'Information sur le prix' })
    ).toBeInTheDocument()
    expect(screen.getByText('The detail of the price')).toBeInTheDocument()
  })

  it('should not display the price details section if the offer has no price details', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        educationalPriceDetail: undefined,
      },
    })

    expect(
      screen.queryByRole('heading', { name: 'Information sur le prix' })
    ).not.toBeInTheDocument()
  })
})
