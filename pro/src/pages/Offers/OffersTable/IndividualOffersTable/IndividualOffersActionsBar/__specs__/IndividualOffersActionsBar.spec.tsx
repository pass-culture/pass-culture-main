import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'

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

describe('ActionsBar', () => {
  let props: IndividualOffersActionsBarProps
  const offerIds = [
    { id: 1, status: OfferStatus.ACTIVE },
    { id: 2, status: OfferStatus.ACTIVE },
  ]

  beforeEach(() => {
    props = {
      canDelete: true,
      canPublish: true,
      canDeactivate: true,
      selectedOffers: offerIds,
      clearSelectedOffers: vi.fn(),
      toggleSelectAllCheckboxes: vi.fn(),
      areAllOffersSelected: false,
      isRestrictedAsAdmin: false,
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
    props.selectedOffers = [{ id: 1, status: OfferStatus.ACTIVE }]

    renderActionsBar(props)

    expect(screen.queryByText('1 offre sélectionnée')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 1 offer are selected', () => {
    renderActionsBar(props)

    expect(screen.queryByText('2 offres sélectionnées')).toBeInTheDocument()
  })

  it('should show a generic count when more than 500 offers are selected', () => {
    props.selectedOffers = Array(501)
      .fill(null)
      .map((val, i) => ({ id: i, status: OfferStatus.ACTIVE }))

    renderActionsBar(props)

    expect(screen.queryByText('500+ offres sélectionnées')).toBeInTheDocument()
  })

  it('should activate selected offers upon publication', async () => {
    renderActionsBar({
      ...props,
      selectedOffers: [
        { id: 1, status: OfferStatus.INACTIVE },
        { id: 2, status: OfferStatus.INACTIVE },
        { id: 3, status: OfferStatus.DRAFT },
      ],
    })

    await userEvent.click(screen.getByText('Publier'))

    expect(api.patchOffersActiveStatus).toHaveBeenLastCalledWith({
      ids: [1, 2],
      isActive: true,
    })
    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText('2 offres ont bien été publiées')
    ).toBeInTheDocument()
  })

  it('should delete selected draft offers upon deletion', async () => {
    renderActionsBar({
      ...props,
      selectedOffers: [
        { id: 1, status: OfferStatus.DRAFT },
        { id: 2, status: OfferStatus.DRAFT },
      ],
    })

    await userEvent.click(screen.getByText('Supprimer'))
    await userEvent.click(screen.getByText('Supprimer ces brouillons'))

    expect(api.deleteDraftOffers).toHaveBeenLastCalledWith({
      ids: [1, 2],
    })
    expect(api.deleteDraftOffers).toHaveBeenCalledTimes(1)
    expect(api.deleteDraftOffers).toHaveBeenNthCalledWith(1, {
      ids: [1, 2],
    })
    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText('2 brouillons ont bien été supprimés')
    ).toBeInTheDocument()
  })

  it('should deactivate selected offers', async () => {
    renderActionsBar({
      ...props,
      areAllOffersSelected: false,
      selectedOffers: [
        { id: 1, status: OfferStatus.ACTIVE },
        { id: 2, status: OfferStatus.SOLD_OUT },
        { id: 3, status: OfferStatus.EXPIRED },
        { id: 4, status: OfferStatus.DRAFT },
        { id: 5, status: OfferStatus.INACTIVE },
      ],
    })

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
      ids: [1, 2, 3],
      isActive: false,
    })
    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)

    expect(
      screen.getByText('3 offres ont bien été désactivées')
    ).toBeInTheDocument()
  })

  it('should unselect offers and hide action bar on click on "Annuler" button', async () => {
    renderActionsBar(props)

    await userEvent.click(screen.getByText('Annuler'))

    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
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
    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
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
    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
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

  it('should not display actions when selected offers have the wrong status', () => {
    props.canDeactivate = false
    props.canPublish = false
    props.canDelete = false

    renderActionsBar(props)

    expect(screen.queryByText('Supprimer')).not.toBeInTheDocument()
    expect(screen.queryByText('Publier')).not.toBeInTheDocument()
    expect(screen.queryByText('Désactiver')).not.toBeInTheDocument()
  })
})
