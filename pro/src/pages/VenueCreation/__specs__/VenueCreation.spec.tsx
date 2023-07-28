import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

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
        isAdmin: false,
        isEmailValidated: true,
        roles: [],
      },
    },
  }

  renderWithProviders(
    <AppLayout>
      <VenueCreation />
    </AppLayout>,
    {
      storeOverrides,
      initialRouterEntries: [`/structures/${offererId}/lieux/creation`],
    }
  )
  await waitFor(() => {
    expect(api.canOffererCreateEducationalOffer).toHaveBeenCalled()
  })
}

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) as object),
  useParams: () => ({
    offererId: '1234',
  }),
}))

Element.prototype.scrollIntoView = vi.fn()

vi.spyOn(window, 'matchMedia').mockReturnValue({
  matches: true,
} as MediaQueryList)

describe('route VenueCreation', () => {
  let offerer: GetOffererResponseModel

  beforeEach(() => {
    offerer = {
      id: 1,
    } as GetOffererResponseModel

    vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
    vi.spyOn(api, 'getVenueTypes').mockResolvedValue([])
    vi.spyOn(api, 'fetchVenueLabels').mockResolvedValue([])
    vi.spyOn(api, 'canOffererCreateEducationalOffer')
  })

  it('should display venue form screen with creation title', async () => {
    // When
    await renderVenueCreation(offerer.id.toString())
    // Then
    const venueCreationTitle = await screen.findByText('Création d’un lieu')
    expect(venueCreationTitle).toBeInTheDocument()
  })

  it('should display modal when user try to quite venue creation', async () => {
    // When
    await renderVenueCreation(offerer.id.toString())
    // Then
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
    // When
    await renderVenueCreation(offerer.id.toString())
    // Then
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
    // When
    await renderVenueCreation(offerer.id.toString())
    // Then
    const homeNavBarButton = await screen.findByText(
      'Enregistrer et créer le lieu'
    )
    await userEvent.click(homeNavBarButton)
    const modal = await screen.queryByText(
      'Voulez-vous quitter la création de lieu ?'
    )
    expect(modal).not.toBeInTheDocument()
  })
})
