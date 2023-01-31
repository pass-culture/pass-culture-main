import { screen } from '@testing-library/react'
import React from 'react'
import { Route } from 'react-router'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import { renderWithProviders } from 'utils/renderWithProviders'

import AppLayout from '../../../app/AppLayout'
import VenueCreation from '../VenueCreation'

const renderVenueCreation = async (offererId: string) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        firstName: 'John',
        dateCreated: '2022-07-29T12:18:43.087097Z',
        email: 'john@do.net',
        id: '1',
        nonHumanizedId: '1',
        isAdmin: false,
        isEmailValidated: true,
        roles: [],
      },
    },
  }

  return renderWithProviders(
    <AppLayout>
      <Route exact path={'/structures/:offererId/lieux/creation'}>
        <VenueCreation />
      </Route>
    </AppLayout>,
    {
      storeOverrides,
      initialRouterEntries: [`/structures/${offererId}/lieux/creation`],
    }
  )
}

jest.mock('apiClient/api', () => ({
  api: {
    fetchVenueLabels: jest.fn(),
    getOfferer: jest.fn(),
    getVenueTypes: jest.fn(),
  },
}))

describe('route VenueCreation', () => {
  let offerer: GetOffererResponseModel

  beforeEach(() => {
    offerer = {
      id: 'ABCD',
    } as GetOffererResponseModel

    jest.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
    jest.spyOn(api, 'getVenueTypes').mockResolvedValue([])
    jest.spyOn(api, 'fetchVenueLabels').mockResolvedValue([])
  })
  it('should display venue form screen with creation title', async () => {
    // When
    await renderVenueCreation(offerer.id)

    // Then
    const venueCreationTitle = await screen.findByText('Création d’un lieu')
    expect(venueCreationTitle).toBeInTheDocument()
  })
  it('should display modal when user try to quite venue creation', async () => {
    // When
    await renderVenueCreation(offerer.id)
    // Then
    const homeNavBarButton = await screen.findByText('Accueil')
    await homeNavBarButton.click()
    const modal = await screen.findByText(
      'Voulez-vous quitter la création de lieu ?'
    )
    expect(modal).toBeInTheDocument()

    const cancelModalButton = await screen.findByText('Annuler')
    await cancelModalButton.click()
    expect(modal).not.toBeInTheDocument()
  })
  it('should display modal when user cancel venue creation', async () => {
    // When
    await renderVenueCreation(offerer.id)
    // Then
    const cancelFormButton = await screen.findByText('Annuler et quitter')
    await cancelFormButton.click()
    const modal = await screen.findByText(
      'Voulez-vous quitter la création de lieu ?'
    )
    expect(modal).toBeInTheDocument()

    const cancelButton = await screen.findByText('Annuler')
    await cancelButton.click()
    expect(modal).not.toBeInTheDocument()
  })
  it('should not display modal when user submit venue creation', async () => {
    // When
    await renderVenueCreation(offerer.id)
    // Then
    const homeNavBarButton = await screen.findByText('Enregistrer et continuer')
    await homeNavBarButton.click()
    const modal = await screen.queryByText(
      'Voulez-vous quitter la création de lieu ?'
    )
    expect(modal).not.toBeInTheDocument()
  })
})
