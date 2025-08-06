import { screen } from '@testing-library/react'

import { CollectiveLocationType } from '@/apiClient//adage'
import { getCollectiveOfferTemplateFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferLocationSection } from '../CollectiveOfferLocationSection'

describe('CollectiveOfferLocationSection', () => {
  it('should display the location address and label when offer is located in a specific address', () => {
    const offer = getCollectiveOfferTemplateFactory()

    renderWithProviders(
      <CollectiveOfferLocationSection
        offer={{
          ...offer,
          location: {
            locationType: CollectiveLocationType.ADDRESS,
            address: {
              label: 'Théâtre de la Corniche',
              city: 'Marseille',
              street: '3 Rue Pimpim',
              postalCode: '13007',
              id_oa: 372,
              isLinkedToVenue: true,
              latitude: 2,
              longitude: 5,
              id: 1234,
              isManualEdition: false,
            },
          },
        }}
      />
    )

    expect(
      screen.getByText('Intitulé : Théâtre de la Corniche')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Adresse : 3 Rue Pimpim, 13007, Marseille')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Zone de mobilité : Paris (75) - Hauts-de-Seine (92)')
    ).not.toBeInTheDocument()
  })

  it('should display the location address without label when offer location has no label provided', () => {
    const offer = getCollectiveOfferTemplateFactory()

    renderWithProviders(
      <CollectiveOfferLocationSection
        offer={{
          ...offer,
          location: {
            locationType: CollectiveLocationType.ADDRESS,
            address: {
              city: 'Marseille',
              street: '3 Rue Pimpim',
              postalCode: '13007',
              id_oa: 372,
              isLinkedToVenue: true,
              latitude: 2,
              longitude: 5,
              id: 1234,
              isManualEdition: false,
            },
          },
        }}
      />
    )

    expect(screen.getByText('Intitulé : -')).toBeInTheDocument()
    expect(
      screen.getByText('Adresse : 3 Rue Pimpim, 13007, Marseille')
    ).toBeInTheDocument()
  })

  it('should display the school and departments information when offer is located school', () => {
    const offer = getCollectiveOfferTemplateFactory()

    renderWithProviders(
      <CollectiveOfferLocationSection
        offer={{
          ...offer,
          interventionArea: ['75', '92'],
          location: {
            locationType: CollectiveLocationType.SCHOOL,
          },
        }}
      />
    )

    expect(
      screen.getByText('Dans l’établissement scolaire')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Zone de mobilité : Paris (75) - Hauts-de-Seine (92)')
    ).toBeInTheDocument()
  })

  it('should display to be defined location information when offer has no location defined', () => {
    const offer = getCollectiveOfferTemplateFactory()

    renderWithProviders(
      <CollectiveOfferLocationSection
        offer={{
          ...offer,
          interventionArea: ['75', '92'],
          location: {
            locationType: CollectiveLocationType.TO_BE_DEFINED,
            locationComment: 'Parlons-en gaiement !',
          },
        }}
      />
    )

    expect(
      screen.getByText('À déterminer avec l’enseignant')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Commentaire : Parlons-en gaiement !')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Zone de mobilité : Paris (75) - Hauts-de-Seine (92)')
    ).toBeInTheDocument()
  })

  it('should display to be defined location information without comment when offer has no location defined and comment is not provided', () => {
    const offer = getCollectiveOfferTemplateFactory()

    renderWithProviders(
      <CollectiveOfferLocationSection
        offer={{
          ...offer,
          interventionArea: ['75', '92'],
          location: {
            locationType: CollectiveLocationType.TO_BE_DEFINED,
          },
        }}
      />
    )

    expect(
      screen.getByText('À déterminer avec l’enseignant')
    ).toBeInTheDocument()
    expect(screen.getByText('Commentaire : -')).toBeInTheDocument()
    expect(
      screen.getByText('Zone de mobilité : Paris (75) - Hauts-de-Seine (92)')
    ).toBeInTheDocument()
  })
})
