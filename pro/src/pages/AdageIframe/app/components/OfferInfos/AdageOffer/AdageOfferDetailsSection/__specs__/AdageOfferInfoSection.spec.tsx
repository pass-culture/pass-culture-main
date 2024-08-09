import { render, screen } from '@testing-library/react'

import { OfferAddressType } from 'apiClient/adage'
import {
  defaultCollectiveTemplateOffer,
  defaultCollectiveOffer,
} from 'utils/adageFactories'

import {
  AdageOfferInfoSection,
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

  it('should show the price section when the offer is bookable', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveOffer,
      },
    })

    expect(
      screen.queryByRole('heading', { name: 'Information sur le prix' })
    ).not.toBeInTheDocument()

    expect(screen.getByRole('heading', { name: 'Prix' })).toBeInTheDocument()

    expect(screen.getByText('1 400 € pour 10 participants')).toBeInTheDocument()
  })

  it('should show the intervention areas', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        interventionArea: ['56', '29'],
        offerVenue: {
          ...defaultCollectiveTemplateOffer.offerVenue,
          addressType: OfferAddressType.OTHER,
        },
      },
    })

    expect(
      screen.getByRole('heading', { name: 'Zone de mobilité' })
    ).toBeInTheDocument()

    expect(screen.getByText('Morbihan (56)')).toBeInTheDocument()
  })
})
