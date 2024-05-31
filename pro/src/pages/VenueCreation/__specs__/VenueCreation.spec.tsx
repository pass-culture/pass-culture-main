import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { VenueCreation } from '../VenueCreation'

const renderVenueCreation = () => {
  renderWithProviders(<VenueCreation />, {
    user: sharedCurrentUserFactory(),
    initialRouterEntries: [
      `/structures/${defaultGetOffererResponseModel.id}/lieux/creation`,
    ],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedOffererId: defaultGetOffererResponseModel.id,
      },
    },
  })
}

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useParams: () => ({
    offererId: defaultGetOffererResponseModel.id.toString(),
  }),
}))
vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

Element.prototype.scrollIntoView = vi.fn()

describe('route VenueCreation', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
    vi.spyOn(api, 'getVenueTypes').mockResolvedValue([])
    vi.spyOn(api, 'fetchVenueLabels').mockResolvedValue([])
  })

  it('should display venue form screen with creation title', async () => {
    renderVenueCreation()

    const venueCreationTitle = await screen.findByText('Création d’un lieu')
    expect(venueCreationTitle).toBeInTheDocument()
  })

  it('should display modal when user try to quite venue creation', async () => {
    renderVenueCreation()

    const homeNavBarButton = await screen.findByText('Accueil')
    await userEvent.click(homeNavBarButton)
    const modal = await screen.findByText(
      'Voulez-vous quitter la création de lieu ?'
    )
    expect(modal).toBeInTheDocument()

    const cancelModalButton = await screen.findByText('Annuler')
    await userEvent.click(cancelModalButton)
    expect(modal).not.toBeInTheDocument()
  })

  it('should display modal when user cancel venue creation', async () => {
    renderVenueCreation()

    const cancelFormButton = await screen.findByText('Annuler et quitter')
    await userEvent.click(cancelFormButton)
    const modal = await screen.findByText(
      'Voulez-vous quitter la création de lieu ?'
    )
    expect(modal).toBeInTheDocument()

    const cancelButton = await screen.findByText('Annuler')
    await userEvent.click(cancelButton)
    expect(modal).not.toBeInTheDocument()
  })

  it('should not display modal when user submit venue creation', async () => {
    renderVenueCreation()

    const homeNavBarButton = await screen.findByText(
      'Enregistrer et créer le lieu'
    )

    await userEvent.click(homeNavBarButton)
    const modal = screen.queryByText(
      'Voulez-vous quitter la création de lieu ?'
    )
    expect(modal).not.toBeInTheDocument()
  })
})
