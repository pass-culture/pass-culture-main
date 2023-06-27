import { screen } from '@testing-library/react'
import { addDays } from 'date-fns'
import React from 'react'

import { DMSApplicationstatus } from 'apiClient/v1'
import {
  defaultCollectiveDmsApplication,
  defaultVenue,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveVenueInformations, {
  CollectiveVenueInformationsProps,
} from '../CollectiveVenueInformations'

const renderCollectiveVenueInformations = (
  props: CollectiveVenueInformationsProps
) => {
  renderWithProviders(<CollectiveVenueInformations {...props} />)
}

describe('CollectiveVenueInformations', () => {
  it('should display description when venue is not accepted on adage', () => {
    renderCollectiveVenueInformations({
      venue: {
        ...defaultVenue,
        collectiveDmsApplication: {
          ...defaultCollectiveDmsApplication,
          state: DMSApplicationstatus.EN_CONSTRUCTION,
        },
      },
      isCreatingVenue: false,
      canCreateCollectiveOffer: false,
    })
    expect(
      screen.getByText(
        'Pour publier des offres à destination des scolaires, votre lieu doit être référencé sur ADAGE, la plateforme dédiée aux enseignants et aux chefs d’établissements.'
      )
    ).toBeInTheDocument()
  })
  it('should display timeline if venue has adage id since less than 30 days', () => {
    renderCollectiveVenueInformations({
      venue: {
        ...defaultVenue,
        hasAdageId: true,
        adageInscriptionDate: addDays(new Date(), -10).toISOString(),
        collectiveDmsApplication: {
          ...defaultCollectiveDmsApplication,
          state: DMSApplicationstatus.ACCEPTE,
        },
      },
      isCreatingVenue: false,
      canCreateCollectiveOffer: true,
    })
    expect(
      screen.getByText(
        'Votre lieu a été ajouté dans ADAGE par le Ministère de l’Education Nationale'
      )
    ).toBeInTheDocument()
  })
  it('should display eac section if venue has adage id since more than 30 days', () => {
    renderCollectiveVenueInformations({
      venue: {
        ...defaultVenue,
        hasAdageId: true,
        adageInscriptionDate: addDays(new Date(), -32).toISOString(),
        collectiveDmsApplication: {
          ...defaultCollectiveDmsApplication,
          state: DMSApplicationstatus.ACCEPTE,
        },
      },
      isCreatingVenue: false,
      canCreateCollectiveOffer: true,
    })
    expect(
      screen.getByRole('heading', {
        name: 'Mes informations pour les enseignants',
      })
    ).toBeInTheDocument()
  })
})
