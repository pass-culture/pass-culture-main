import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Notification } from 'components/Notification/Notification'
import { Events } from 'core/FirebaseEvents/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  IndividualOffersActionsBar,
  IndividualOffersActionsBarProps,
} from '../IndividualOffersActionsBar'

const renderActionsBar = (props: IndividualOffersActionsBarProps) => {
  renderWithProviders(
    <>
      <IndividualOffersActionsBar {...props} />
      <Notification />
    </>,
    { storeOverrides: {}, initialRouterEntries: ['/offres'] }
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

describe('ActionsBar', () => {
  let props: IndividualOffersActionsBarProps
  const offerIds = [1, 2]

  beforeEach(() => {
    props = {
      getUpdateOffersStatusMessage: mockGetUpdateOffersStatusMessage,
      canDeleteOffers: true,
      selectedOfferIds: offerIds,
      clearSelectedOfferIds: vi.fn(),
      toggleSelectAllCheckboxes: vi.fn(),
      areAllOffersSelected: false,
    }
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
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
    props.selectedOfferIds = [1]

    renderActionsBar(props)

    expect(screen.queryByText('1 offre sélectionnée')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 1 offer are selected', () => {
    renderActionsBar(props)

    expect(screen.queryByText('2 offres sélectionnées')).toBeInTheDocument()
  })

  it('should show a generic count when more than 500 offers are selected', () => {
    props.selectedOfferIds = Array(501)
      .fill(null)
      .map((val, i) => i)

    renderActionsBar(props)

    expect(screen.queryByText('500+ offres sélectionnées')).toBeInTheDocument()
  })

  it('should activate selected offers upon publication', async () => {
    renderActionsBar(props)

    await userEvent.click(screen.getByText('Publier'))

    expect(api.patchOffersActiveStatus).toHaveBeenLastCalledWith({
      ids: [1, 2],
      isActive: true,
    })
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
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
      ids: [1, 2],
    })
    expect(api.deleteDraftOffers).toHaveBeenCalledTimes(1)
    expect(api.deleteDraftOffers).toHaveBeenNthCalledWith(1, {
      ids: [1, 2],
    })
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText('Les brouillons ont bien été supprimés')
    ).toBeInTheDocument()
  })

  it('should not delete offers when a non draft is selected upon deletion', async () => {
    props.canDeleteOffers = false

    renderActionsBar(props)

    await userEvent.click(screen.getByText('Supprimer'))

    expect(api.patchOffersActiveStatus).not.toHaveBeenCalled()
    expect(props.clearSelectedOfferIds).not.toHaveBeenCalled()
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
      ids: [1, 2],
      isActive: false,
    })
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)

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

    const expectedBody = {
      isActive: true,
    }

    const activateButton = screen.getByText('Publier')
    await userEvent.click(activateButton)

    expect(api.patchAllOffersActiveStatus).toHaveBeenLastCalledWith(
      expectedBody
    )
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
  })

  it('should deactivate all offers on click on "Désactiver" button when all offers are selected', async () => {
    props.areAllOffersSelected = true
    renderActionsBar(props)

    const expectedBody = {
      isActive: false,
    }

    const deactivateButton = screen.getByText('Désactiver')
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

  it('should show an error message when an error occurs after clicking on "Publier" button when all offers are selected', async () => {
    props.areAllOffersSelected = true
    vi.spyOn(api, 'patchAllOffersActiveStatus').mockRejectedValueOnce(null)
    renderActionsBar(props)

    const activateButton = screen.getByText('Publier')
    await userEvent.click(activateButton)

    expect(
      screen.getByText(
        'Une erreur est survenue lors de l’activation des offres'
      )
    )
  })

  it('should show an error message when an error occurs after clicking on "Publier" button when some offers are selected', async () => {
    vi.spyOn(api, 'patchOffersActiveStatus').mockRejectedValueOnce(null)
    renderActionsBar(props)

    const activateButton = screen.getByText('Publier')
    await userEvent.click(activateButton)

    expect(
      screen.getByText(
        'Une erreur est survenue lors de l’activation des offres'
      )
    )
  })

  it('should show an error message when an error occurs after clicking on "Supprimer" button when some offers are selected', async () => {
    vi.spyOn(api, 'deleteDraftOffers').mockRejectedValueOnce(null)
    renderActionsBar(props)

    const activateButton = screen.getByText('Supprimer')
    await userEvent.click(activateButton)

    await userEvent.click(screen.getByText('Supprimer ces brouillons'))

    expect(
      screen.getByText(
        'Une erreur est survenue lors de la suppression des brouillon'
      )
    )
  })
})
