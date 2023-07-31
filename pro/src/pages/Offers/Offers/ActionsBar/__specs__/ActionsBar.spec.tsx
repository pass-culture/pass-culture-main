import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import Notification from 'components/Notification/Notification'
import { Events } from 'core/FirebaseEvents/constants'
import { Audience } from 'core/shared'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import ActionsBar, { ActionBarProps } from '../ActionsBar'

const renderActionsBar = (props: ActionBarProps) => {
  const storeOverrides = {
    offers: {
      searchFilters: {
        nameOrIsbn: 'keyword',
        venueId: 'E3',
        offererId: 'A4',
      },
    },
  }

  renderWithProviders(
    <>
      <ActionsBar {...props} />
      <Notification />
    </>,
    { storeOverrides, initialRouterEntries: ['/offres'] }
  )
}

vi.mock('apiClient/api', () => ({
  api: {
    patchOffersActiveStatus: vi.fn(),
    deleteDraftOffers: vi.fn(),
    patchAllOffersActiveStatus: vi.fn(),
  },
}))

const mockLogEvent = vi.fn()
const mockGetUpdateOffersStatusMessage = vi.fn()
const mockCanDeleteOffers = vi.fn(() => true)

describe('ActionsBar', () => {
  let props: ActionBarProps
  const offerIds = ['1', '2']

  beforeEach(() => {
    props = {
      getUpdateOffersStatusMessage: mockGetUpdateOffersStatusMessage,
      canDeleteOffers: mockCanDeleteOffers,
      refreshOffers: vi.fn(),
      selectedOfferIds: offerIds,
      clearSelectedOfferIds: vi.fn(),
      toggleSelectAllCheckboxes: vi.fn(),
      nbSelectedOffers: 2,
      areAllOffersSelected: false,
      audience: Audience.INDIVIDUAL,
    }
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should have buttons to activate and deactivate offers, to delete, and to abort action', () => {
    renderActionsBar(props)

    screen.getByText('Publier', { selector: 'button' })

    expect(
      screen.queryByText('Publier', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Désactiver', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Supprimer', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Annuler', { selector: 'button' })
    ).toBeInTheDocument()
  })

  it('should say how many offers are selected when only 1 offer is selected', () => {
    props.nbSelectedOffers = 1

    renderActionsBar(props)

    expect(screen.queryByText('1 offre sélectionnée')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 1 offer are selected', () => {
    renderActionsBar(props)

    expect(screen.queryByText('2 offres sélectionnées')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 500 offers are selected', () => {
    props.nbSelectedOffers = 501

    renderActionsBar(props)

    expect(screen.queryByText('500+ offres sélectionnées')).toBeInTheDocument()
  })

  it('should activate selected offers upon publication', async () => {
    renderActionsBar(props)

    await userEvent.click(screen.getByText('Publier'))

    expect(api.patchOffersActiveStatus).toHaveBeenLastCalledWith({
      ids: offerIds,
      isActive: true,
    })
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
    expect(props.refreshOffers).toHaveBeenCalled()
    expect(
      screen.getByText('2 offres ont bien été publiées')
    ).toBeInTheDocument()
  })

  it('should not activate offers when a draft is selected', async () => {
    mockGetUpdateOffersStatusMessage.mockReturnValueOnce(
      'Vous ne pouvez pas publier des brouillons depuis cette liste'
    )

    renderActionsBar(props)

    await userEvent.click(screen.getByText('Publier'))

    expect(api.patchOffersActiveStatus).not.toHaveBeenCalled()
    expect(props.clearSelectedOfferIds).not.toHaveBeenCalled()
    expect(props.refreshOffers).not.toHaveBeenCalled()
    expect(
      screen.getByText(
        'Vous ne pouvez pas publier des brouillons depuis cette liste'
      )
    ).toBeInTheDocument()
  })

  it('should delete selected draft offers upon deletion', async () => {
    renderActionsBar(props)

    await userEvent.click(screen.getByText('Supprimer'))
    await userEvent.click(screen.getByText('Supprimer ces brouillons'))

    expect(api.deleteDraftOffers).toHaveBeenLastCalledWith({
      ids: offerIds,
    })
    expect(api.deleteDraftOffers).toHaveBeenCalledTimes(1)
    expect(api.deleteDraftOffers).toHaveBeenNthCalledWith(1, {
      ids: offerIds,
    })
    expect(props.refreshOffers).toHaveBeenCalledTimes(1)
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText('2 brouillons ont bien été supprimés')
    ).toBeInTheDocument()
  })

  it('should not delete offers when a non draft is selected upon deletion', async () => {
    mockCanDeleteOffers.mockReturnValueOnce(false)

    renderActionsBar(props)

    await userEvent.click(screen.getByText('Supprimer'))

    expect(api.patchOffersActiveStatus).not.toHaveBeenCalled()
    expect(props.clearSelectedOfferIds).not.toHaveBeenCalled()
    expect(props.refreshOffers).not.toHaveBeenCalled()
    expect(
      screen.getByText('Seuls les brouillons peuvent être supprimés')
    ).toBeInTheDocument()
  })

  it('should deactivate selected offers', async () => {
    props.areAllOffersSelected = false
    renderActionsBar(props)

    await userEvent.click(screen.getByText('Désactiver'))
    const confirmDeactivateButton = screen.getAllByText('Désactiver')[1]
    await userEvent.click(confirmDeactivateButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DISABLED_SELECTED_OFFERS,
      {
        from: '/offres',
        has_selected_all_offers: false,
      }
    )
    expect(api.patchOffersActiveStatus).toHaveBeenLastCalledWith({
      ids: offerIds,
      isActive: false,
    })
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
    expect(props.refreshOffers).toHaveBeenCalledWith()

    expect(
      screen.getByText('2 offres ont bien été désactivées')
    ).toBeInTheDocument()
  })

  it('should unselect offers and hide action bar on click on "Annuler" button', async () => {
    renderActionsBar(props)

    await userEvent.click(screen.getByText('Annuler'))

    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
  })

  it('should activate all offers on click on "Publier" button when all offers are selected', async () => {
    props.areAllOffersSelected = true

    renderActionsBar(props)
    const activateButton = screen.getByText('Publier')
    const expectedBody = {
      isActive: true,
      nameOrIsbn: 'keyword',
      offererId: 'A4',
      venueId: 'E3',
    }

    await userEvent.click(activateButton)

    expect(api.patchAllOffersActiveStatus).toHaveBeenLastCalledWith(
      expectedBody
    )
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
    expect(props.refreshOffers).toHaveBeenCalledWith()
  })

  it('should deactivate all offers on click on "Désactiver" button when all offers are selected', async () => {
    props.areAllOffersSelected = true
    renderActionsBar(props)
    const deactivateButton = screen.getByText('Désactiver')
    const expectedBody = {
      isActive: false,
      nameOrIsbn: 'keyword',
      offererId: 'A4',
      venueId: 'E3',
    }

    await userEvent.click(deactivateButton)
    const confirmDeactivateButton = screen.getAllByText('Désactiver')[1]
    await userEvent.click(confirmDeactivateButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DISABLED_SELECTED_OFFERS,
      {
        from: '/offres',
        has_selected_all_offers: true,
      }
    )
    expect(api.patchAllOffersActiveStatus).toHaveBeenLastCalledWith(
      expectedBody
    )
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
    expect(props.refreshOffers).toHaveBeenCalledWith()
  })

  it('should track cancel all offers on click on "Annuler" button', async () => {
    props.areAllOffersSelected = true
    renderActionsBar(props)
    const deactivateButton = screen.getByText('Désactiver')

    await userEvent.click(deactivateButton)
    const cancelDeactivateButton = screen.getAllByText('Annuler')[1]
    await userEvent.click(cancelDeactivateButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_CANCELED_SELECTED_OFFERS,
      {
        from: '/offres',
        has_selected_all_offers: true,
      }
    )
  })

  it('should track cancel offer on click on "Annuler" button', async () => {
    props.areAllOffersSelected = false
    renderActionsBar(props)
    const deactivateButton = screen.getByText('Désactiver')

    await userEvent.click(deactivateButton)
    const cancelDeactivateButton = screen.getAllByText('Annuler')[1]
    await userEvent.click(cancelDeactivateButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_CANCELED_SELECTED_OFFERS,
      {
        from: '/offres',
        has_selected_all_offers: false,
      }
    )
  })
})
