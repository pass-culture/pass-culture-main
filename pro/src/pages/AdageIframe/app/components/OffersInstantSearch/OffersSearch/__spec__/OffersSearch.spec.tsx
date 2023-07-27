import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { AdageFrontRoles, AuthenticatedResponse } from 'apiClient/adage'
import {
  AlgoliaQueryContextProvider,
  FiltersContextProvider,
} from 'pages/AdageIframe/app/providers'
import { AdageUserContext } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffersSearchComponent, SearchProps } from '../OffersSearch'

vi.mock('../Offers/Offers', () => {
  return {
    Offers: jest.fn(() => <div />),
  }
})

vi.mock('apiClient/api', () => ({
  apiAdage: {
    getEducationalOffersCategories: vi.fn(),
  },
}))

vi.mock('pages/AdageIframe/repository/pcapi/pcapi', () => ({
  getEducationalDomains: jest
    .fn()
    .mockResolvedValue([{ id: 1, name: 'Architecture' }]),
}))

const renderOffersSearchComponent = (
  props: SearchProps,
  user: AuthenticatedResponse
) => {
  renderWithProviders(
    <AdageUserContext.Provider value={{ adageUser: user }}>
      <FiltersContextProvider>
        <AlgoliaQueryContextProvider>
          <OffersSearchComponent {...props} />
        </AlgoliaQueryContextProvider>
      </FiltersContextProvider>
    </AdageUserContext.Provider>
  )
}

describe('offersSearch component', () => {
  let props: SearchProps
  const user = {
    role: AdageFrontRoles.REDACTOR,
    uai: 'uai',
    departmentCode: '30',
    institutionName: 'COLLEGE BELLEVUE',
    institutionCity: 'ALES',
  }

  beforeEach(() => {
    props = {
      removeVenueFilter: vi.fn(),
      venueFilter: null,
      refine: vi.fn(),
      currentRefinement: '',
      isSearchStalled: false,
    }
  })

  it('should call algolia with requested query and uai all', async () => {
    // Given
    renderOffersSearchComponent(props, user)
    const launchSearchButton = screen.getByRole('button', {
      name: 'Rechercher',
    })

    // When
    const textInput = screen.getByPlaceholderText(
      'Rechercher : nom de l’offre, partenaire culturel'
    )
    await userEvent.type(textInput, 'Paris')
    await userEvent.click(launchSearchButton)

    // Then
    expect(props.refine).toHaveBeenCalledWith('Paris')
  })

  it('should call algolia after clear all filters', async () => {
    // Given
    renderOffersSearchComponent(props, user)
    const clearFilterButton = screen.getByRole('button', {
      name: 'Effacer les filtres',
    })

    // When
    const textInput = screen.getByPlaceholderText(
      'Rechercher : nom de l’offre, partenaire culturel'
    )
    await userEvent.type(textInput, 'Paris')
    await userEvent.click(clearFilterButton)

    // Then
    expect(props.refine).toHaveBeenCalledWith('')
  })

  it('should call algolia with requested query and uai associatedToInstitution', async () => {
    // Given
    renderOffersSearchComponent(props, {
      ...user,
      uai: 'associatedToInstitution',
    })
    const launchSearchButton = screen.getByRole('button', {
      name: 'Rechercher',
    })

    // When
    const textInput = screen.getByPlaceholderText(
      'Rechercher : nom de l’offre, partenaire culturel'
    )
    await userEvent.type(textInput, 'Paris')
    await userEvent.click(launchSearchButton)

    // Then
    expect(props.refine).toHaveBeenCalledWith('Paris')
  })

  it('should call algolia after clear all filters', async () => {
    // Given
    renderOffersSearchComponent(props, {
      ...user,
      uai: 'assicatedToInstitution',
    })
    const clearFilterButton = screen.getByRole('button', {
      name: 'Effacer les filtres',
    })

    // When
    const textInput = screen.getByPlaceholderText(
      'Rechercher : nom de l’offre, partenaire culturel'
    )
    await userEvent.type(textInput, 'Paris')
    await userEvent.click(clearFilterButton)

    // Then
    expect(props.refine).toHaveBeenCalledWith('')
  })
})
