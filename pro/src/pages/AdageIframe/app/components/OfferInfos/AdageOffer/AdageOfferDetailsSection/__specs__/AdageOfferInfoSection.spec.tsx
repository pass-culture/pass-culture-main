import { screen } from '@testing-library/react'
import { expect } from 'vitest'

import { CollectiveLocationType, OfferAddressType } from 'apiClient/adage'
import {
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
} from 'commons/utils/factories/adageFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import {
  AdageOfferInfoSection,
  AdageOfferInfoSectionProps,
} from '../AdageOfferInfoSection'

function renderAdageOfferInfoSection(
  props: AdageOfferInfoSectionProps = {
    offer: defaultCollectiveTemplateOffer,
  },
  options?: RenderWithProvidersOptions
) {
  return renderWithProviders(<AdageOfferInfoSection {...props} />, options)
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
      screen.getByRole('heading', { name: 'Localisation de l’offre' })
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
describe('OA feature flag', () => {
  it('should display the right wording without the OA FF', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveOffer,
      },
    })
    expect(screen.getByText('Localisation de l’offre')).toBeInTheDocument()
  })

  it('should display the right address when location type is address', () => {
    renderAdageOfferInfoSection(
      {
        offer: {
          ...defaultCollectiveTemplateOffer,
          location: {
            locationType: CollectiveLocationType.ADDRESS,
            address: {
              id: 1,
              id_oa: 1,
              isManualEdition: false,
              latitude: 48.8566,
              longitude: 2.3522,
              label: 'Label',
              street: '123 Rue de Meaux',
              city: 'Paris',
              postalCode: '75000',
            },
          },
        },
      },
      { features: ['WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'] }
    )

    expect(
      screen.getByText('Label - 123 Rue de Meaux, 75000, Paris')
    ).toBeInTheDocument()
  })

  it('should display the right wording when location type is to be defined', () => {
    renderAdageOfferInfoSection(
      {
        offer: {
          ...defaultCollectiveTemplateOffer,
          location: {
            locationType: CollectiveLocationType.TO_BE_DEFINED,
            locationComment: 'Test comment section',
          },
        },
      },
      { features: ['WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'] }
    )

    expect(
      screen.getByText('À déterminer avec l’enseignant')
    ).toBeInTheDocument()
    expect(screen.getByText('Commentaire')).toBeInTheDocument()
    expect(screen.getByText('Test comment section')).toBeInTheDocument()
  })

  it.each([null, undefined, ''])(
    'should not display comment section when location type is to be defined and comment is empty',
    (comment) => {
      renderAdageOfferInfoSection(
        {
          offer: {
            ...defaultCollectiveTemplateOffer,
            location: {
              locationType: CollectiveLocationType.TO_BE_DEFINED,
              locationComment: comment,
            },
          },
        },
        { features: ['WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'] }
      )

      expect(
        screen.getByText('À déterminer avec l’enseignant')
      ).toBeInTheDocument()
      expect(screen.queryByText('Commentaire')).toBeNull()
    }
  )

  it('should display the right wording when location type is school', () => {
    renderAdageOfferInfoSection(
      {
        offer: {
          ...defaultCollectiveTemplateOffer,
          location: {
            locationType: CollectiveLocationType.SCHOOL,
          },
        },
      },
      { features: ['WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'] }
    )

    expect(
      screen.getByText(
        'Le partenaire culturel se déplace dans les établissements scolaires.'
      )
    ).toBeInTheDocument()
  })
})
