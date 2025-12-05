import { screen } from '@testing-library/react'
import { expect } from 'vitest'

import { CollectiveLocationType } from '@/apiClient/adage'
import {
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
} from '@/commons/utils/factories/adageFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  AdageOfferInfoSection,
  type AdageOfferInfoSectionProps,
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

  it('should display the offer price details for a bookable offer', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveOffer,
        educationalPriceDetail: 'The detail of the price',
        stock: {
          ...defaultCollectiveOffer.stock,
          educationalPriceDetail: 'Price details for bookable offer',
        },
      },
    })

    expect(screen.getByRole('heading', { name: 'Prix' })).toBeInTheDocument()
    expect(
      screen.getByText('Price details for bookable offer')
    ).toBeInTheDocument()
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

  it('should display the right address when location type is address', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        location: {
          locationType: CollectiveLocationType.ADDRESS,
          location: {
            id: 1,
            isVenueLocation: false,
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
    })

    expect(
      screen.getByText('Label - 123 Rue de Meaux, 75000, Paris')
    ).toBeInTheDocument()
  })

  it('should display the right wording when location type is to be defined', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        location: {
          locationType: CollectiveLocationType.TO_BE_DEFINED,
          locationComment: 'Test comment section',
        },
      },
    })

    expect(
      screen.getByText('À déterminer avec l’enseignant')
    ).toBeInTheDocument()
    expect(screen.getByText('Commentaire')).toBeInTheDocument()
    expect(screen.getByText('Test comment section')).toBeInTheDocument()
  })

  it.each([
    null,
    undefined,
    '',
  ])('should not display comment section when location type is to be defined and comment is empty', (comment) => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        location: {
          locationType: CollectiveLocationType.TO_BE_DEFINED,
          locationComment: comment,
        },
      },
    })

    expect(
      screen.getByText('À déterminer avec l’enseignant')
    ).toBeInTheDocument()
    expect(screen.queryByText('Commentaire')).toBeNull()
  })

  it('should display the right wording when location type is school', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        location: {
          locationType: CollectiveLocationType.SCHOOL,
        },
      },
    })

    expect(
      screen.getByText(
        'Le partenaire culturel se déplace dans les établissements scolaires.'
      )
    ).toBeInTheDocument()
  })

  it('should not display dash when address has no label', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        location: {
          locationType: CollectiveLocationType.ADDRESS,
          location: {
            id: 1,
            isVenueLocation: false,
            isManualEdition: false,
            latitude: 48.8566,
            longitude: 2.3522,
            label: undefined,
            street: '123 Rue de Meaux',
            city: 'Paris',
            postalCode: '75000',
          },
        },
      },
    })

    expect(
      screen.getByText('123 Rue de Meaux, 75000, Paris')
    ).toBeInTheDocument()
  })
})
