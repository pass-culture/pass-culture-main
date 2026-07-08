import { screen } from '@testing-library/react'
import { expect } from 'vitest'

import {
  CollectiveAdditionalFeeType,
  CollectiveLocationType,
} from '@/apiClient/adage'
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

const defaultProps: AdageOfferInfoSectionProps = {
  offer: defaultCollectiveTemplateOffer,
}

function renderAdageOfferInfoSection(
  props: AdageOfferInfoSectionProps = defaultProps,
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
    ).toBeVisible()
    expect(screen.getByText('The detail of the price')).toBeVisible()
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

    expect(screen.getByRole('heading', { name: 'Prix' })).toBeVisible()
    expect(screen.getByText('Price details for bookable offer')).toBeVisible()
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

    expect(screen.getByRole('heading', { name: 'Prix' })).toBeVisible()

    expect(screen.getByText('1 400 € pour 10 participants')).toBeVisible()
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
    ).toBeVisible()
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

    expect(screen.getByText('À déterminer avec l’enseignant')).toBeVisible()
    expect(screen.getByText('Commentaire')).toBeVisible()
    expect(screen.getByText('Test comment section')).toBeVisible()
  })

  it.each([
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

    expect(screen.getByText('À déterminer avec l’enseignant')).toBeVisible()
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
    ).toBeVisible()
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

    expect(screen.getByText('123 Rue de Meaux, 75000, Paris')).toBeVisible()
  })

  describe('WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS', () => {
    const ffOptions: RenderWithProvidersOptions = {
      features: ['WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'],
    }

    it('should display total price TTC only when no additional fees', () => {
      renderAdageOfferInfoSection(
        {
          offer: {
            ...defaultCollectiveOffer,
            stock: {
              ...defaultCollectiveOffer.stock,
              price: 10000,
              servicePrice: 10000,
              collectiveAdditionalFees: [],
            },
          },
        },
        ffOptions
      )

      expect(screen.getByText(/Prix total TTC : 100 €/)).toBeVisible()
      expect(
        screen.queryByText(/Dont le tarif de la prestation : 100 €/)
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText(/Dont les frais annexes/)
      ).not.toBeInTheDocument()
    })

    it('should display price breakdown when additional fees exist', () => {
      renderAdageOfferInfoSection(
        {
          offer: {
            ...defaultCollectiveOffer,
            stock: {
              ...defaultCollectiveOffer.stock,
              price: 14500,
              servicePrice: 10000,
              collectiveAdditionalFees: [
                {
                  // TODO: (jcicurel 2026-07-08) the label should be null
                  // but for now the schema has label?: string
                  // when the backend model is migrated it should be label: string | null
                  type: CollectiveAdditionalFeeType.TRAVEL,
                  amount: 3000,
                },
                {
                  type: CollectiveAdditionalFeeType.MEAL,
                  amount: 1500,
                },
                {
                  type: CollectiveAdditionalFeeType.OTHER,
                  label: 'Annexe',
                  amount: 1515,
                },
              ],
            },
          },
        },
        ffOptions
      )

      expect(screen.getByText(/Prix total TTC : 145 €/)).toBeVisible()
      expect(
        screen.getByText(/Dont le tarif de la prestation : 100 €/)
      ).toBeVisible()
      expect(screen.getByText(/Dont les frais annexes/)).toBeVisible()
      expect(
        screen.getByText(/Déplacement de l'intervenant•e : 30 €/)
      ).toBeVisible()
      expect(screen.getByText(/Repas de l'intervenant•e : 15 €/)).toBeVisible()
      expect(screen.getByText(/Annexe : 15,15 €/)).toBeVisible()
    })

    it('should display informations pratiques section when additionalDetails exists', () => {
      renderAdageOfferInfoSection(
        {
          offer: {
            ...defaultCollectiveOffer,
            additionalDetails: "Détail pratique de l'offre",
            stock: {
              ...defaultCollectiveOffer.stock,
              educationalPriceDetail: 'Détail du prix', // check that we do not read the old field
            },
          },
        },
        ffOptions
      )

      expect(
        screen.getByRole('heading', { name: 'Informations pratiques' })
      ).toBeVisible()
      expect(screen.getByText("Détail pratique de l'offre")).toBeVisible()
    })

    it('should not display informations pratiques section when additionalDetails is absent', () => {
      renderAdageOfferInfoSection(
        {
          offer: {
            ...defaultCollectiveOffer,
            additionalDetails: undefined,
            stock: {
              ...defaultCollectiveOffer.stock,
              educationalPriceDetail: 'prix',
            },
          },
        },
        ffOptions
      )

      expect(
        screen.queryByRole('heading', { name: 'Informations pratiques' })
      ).not.toBeInTheDocument()
    })
  })
})
