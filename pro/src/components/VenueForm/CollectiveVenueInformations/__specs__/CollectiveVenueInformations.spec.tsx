import { screen } from '@testing-library/react'
import { addDays } from 'date-fns'
import React from 'react'

import {
  defaultCollectiveDmsApplication,
  defaultIVenue,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { DMS_STATUS } from '../CollectiveDmsTimeline/CollectiveDmsTimeline'
import CollectiveVenueInformations, {
  ICollectiveVenueInformationsProps,
} from '../CollectiveVenueInformations'

const renderCollectiveVenueInformations = (
  props: ICollectiveVenueInformationsProps
) => {
  renderWithProviders(<CollectiveVenueInformations {...props} />)
}

describe('CollectiveVenueInformations', () => {
  it('should display description when venue is not accepted on adage', () => {
    renderCollectiveVenueInformations({
      venue: {
        ...defaultIVenue,
        collectiveDmsApplication: {
          ...defaultCollectiveDmsApplication,
          state: DMS_STATUS.DRAFT,
        },
      },
      isCreatingVenue: false,
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
        ...defaultIVenue,
        hasAdageId: true,
        adageInscriptionDate: addDays(new Date(), -10).toISOString(),
        collectiveDmsApplication: {
          ...defaultCollectiveDmsApplication,
          state: 'ADDED_IN_ADAGE',
        },
      },
      isCreatingVenue: false,
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
        ...defaultIVenue,
        hasAdageId: true,
        adageInscriptionDate: addDays(new Date(), -32).toISOString(),
        collectiveDmsApplication: {
          ...defaultCollectiveDmsApplication,
          state: DMS_STATUS.ADDED_IN_ADAGE,
        },
      },
      isCreatingVenue: false,
    })
    expect(
      screen.getByRole('heading', {
        name: 'Mes informations pour les enseignants',
      })
    ).toBeInTheDocument()
  })
})
