import { screen, within } from '@testing-library/react'
import React from 'react'

import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueList, VenueListProps } from '../VenueList'

const renderVenueList = (props: Partial<VenueListProps> = {}) => {
  renderWithProviders(
    <VenueList offerer={defaultGetOffererResponseModel} {...props} />
  )
}

const virtualVenue = {
  ...defaultGetOffererVenueResponseModel,
  id: 1,
  isVirtual: true,
  name: 'Le Sous-sol (Offre numérique)',
  publicName: null,
}
const physicalVenue = {
  ...defaultGetOffererVenueResponseModel,
  id: 2,
  isVirtual: false,
  name: 'Le Sous-sol (Offre physique)',
  publicName: null,
}
const physicalVenueWithPublicName = {
  ...defaultGetOffererVenueResponseModel,
  id: 3,
  isVirtual: false,
  name: 'Le deuxième Sous-sol (Offre physique)',
  publicName: 'Le deuxième Sous-sol',
}

describe('VenueList', () => {
  it('should display offerer venues informations', () => {
    const offerer = {
      ...defaultGetOffererResponseModel,
      hasDigitalVenueAtLeastOneOffer: true,
      managedVenues: [virtualVenue, physicalVenue, physicalVenueWithPublicName],
    }
    renderVenueList({ offerer })

    const virtualVenueTitle = screen.getByText('Offres numériques')
    expect(virtualVenueTitle).toBeInTheDocument()
    const physicalVenueTitle = screen.getByText(physicalVenue.name)
    expect(physicalVenueTitle).toBeInTheDocument()
    const physicalVenueContainer = physicalVenueTitle.closest('div')
    expect(
      physicalVenueContainer &&
        within(physicalVenueContainer).getByText('Gérer ma page', {
          exact: false,
        })
    ).toBeInTheDocument()

    const secondOfflineVenueTitle = screen.getByText('Le deuxième Sous-sol')
    expect(secondOfflineVenueTitle).toBeInTheDocument()
  })

  it('should not display virtual venue informations when no virtual offers', () => {
    const offerer = {
      ...defaultGetOffererResponseModel,
      managedVenues: [virtualVenue, physicalVenue, physicalVenueWithPublicName],
    }
    renderVenueList({ offerer })

    expect(screen.queryByText('Offre numérique')).not.toBeInTheDocument()
  })
})
