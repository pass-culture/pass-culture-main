import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

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
      isCreatingVenue: false,
    })
    expect(
      screen.getByText(
        'Pour publier des offres à destination des scolaires, votre lieu doit être référencé sur ADAGE, la plateforme dédiée aux enseignants et aux chefs d’établissements.'
      )
    ).toBeInTheDocument()
  })
})
