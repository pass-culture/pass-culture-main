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

jest.mock('apiClient/api', () => ({
  api: {
    patchOffersActiveStatus: jest.fn().mockResolvedValue({}),
    deleteDraftOffers: jest.fn().mockResolvedValue({}),
    patchAllOffersActiveStatus: jest.fn().mockResolvedValue({}),
  },
}))

const mockLogEvent = jest.fn()
const mockGetUpdateOffersStatusMessage = jest.fn().mockReturnValue('')
const mockCanDeleteOffers = jest.fn().mockReturnValue(true)

describe('src | components | pages | Offers | ActionsBar', () => {
  let props: ActionBarProps
  const offerIds = ['1', '2']

  beforeEach(() => {
    props = {
      getUpdateOffersStatusMessage: mockGetUpdateOffersStatusMessage,
      canDeleteOffers: mockCanDeleteOffers,
      refreshOffers: jest.fn(),
      selectedOfferIds: offerIds,
      clearSelectedOfferIds: jest.fn(),
      toggleSelectAllCheckboxes: jest.fn(),
      nbSelectedOffers: 2,
      areAllOffersSelected: false,
      audience: Audience.INDIVIDUAL,
    }
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should have buttons to activate and deactivate offers, to delete, and to abort action', () => {
    // when
    renderActionsBar(props)

    screen.getByText('Publier', { selector: 'button' })

    // then
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
    // given
    props.nbSelectedOffers = 1

    // when
    renderActionsBar(props)

    // then
    expect(screen.queryByText('1 offre sélectionnée')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 1 offer are selected', () => {
    // when
    renderActionsBar(props)

    // then
    expect(screen.queryByText('2 offres sélectionnées')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 500 offers are selected', () => {
    // given
    props.nbSelectedOffers = 501

    // when
    renderActionsBar(props)

    // then
    expect(screen.queryByText('500+ offres sélectionnées')).toBeInTheDocument()
  })

  describe('on click on "Publier" button', () => {
    it('should activate selected offers', async () => {
      // given
      renderActionsBar(props)

      // when
      await userEvent.click(screen.getByText('Publier'))

      // then
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
      // given
      mockGetUpdateOffersStatusMessage.mockReturnValueOnce(
        'Vous ne pouvez pas publier des brouillons depuis cette liste'
      )

      renderActionsBar(props)

      // when
      await userEvent.click(screen.getByText('Publier'))

      // then
      expect(api.patchOffersActiveStatus).not.toHaveBeenCalled()
      expect(props.clearSelectedOfferIds).not.toHaveBeenCalled()
      expect(props.refreshOffers).not.toHaveBeenCalled()
      expect(
        screen.getByText(
          'Vous ne pouvez pas publier des brouillons depuis cette liste'
        )
      ).toBeInTheDocument()
    })
  })
  describe('on click on "Supprimer" button', () => {
    it('should delete selected draft offers', async () => {
      // given
      renderActionsBar(props)

      // when
      await userEvent.click(screen.getByText('Supprimer'))
      await userEvent.click(screen.getByText('Supprimer ces brouillons'))

      // then
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
    it('should not delete offers when a non draft is selected', async () => {
      // given

      mockCanDeleteOffers.mockReturnValueOnce(false)

      renderActionsBar(props)

      // when
      await userEvent.click(screen.getByText('Supprimer'))

      // then
      expect(api.patchOffersActiveStatus).not.toHaveBeenCalled()
      expect(props.clearSelectedOfferIds).not.toHaveBeenCalled()
      expect(props.refreshOffers).not.toHaveBeenCalled()
      expect(
        screen.getByText('Seuls les brouillons peuvent être supprimés')
      ).toBeInTheDocument()
    })
  })

  describe('on click on "Désactiver" button', () => {
    it('should deactivate selected offers', async () => {
      // given
      props.areAllOffersSelected = false
      renderActionsBar(props)

      // when
      await userEvent.click(screen.getByText('Désactiver'))
      const confirmDeactivateButton = screen.getAllByText('Désactiver')[1]
      await userEvent.click(confirmDeactivateButton)

      // then
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
  })

  it('should unselect offers and hide action bar on click on "Annuler" button', async () => {
    // given
    renderActionsBar(props)

    // when
    await userEvent.click(screen.getByText('Annuler'))

    // then
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
  })

  describe('when all offers are selected', () => {
    it('should activate all offers on click on "Publier" button', async () => {
      // given
      props.areAllOffersSelected = true

      renderActionsBar(props)
      const activateButton = screen.getByText('Publier')
      const expectedBody = {
        isActive: true,
        nameOrIsbn: 'keyword',
        offererId: 'A4',
        venueId: 'E3',
      }

      // when
      await userEvent.click(activateButton)

      // then
      expect(api.patchAllOffersActiveStatus).toHaveBeenLastCalledWith(
        expectedBody
      )
      expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
      expect(props.refreshOffers).toHaveBeenCalledWith()
    })
    it('should deactivate all offers on click on "Désactiver" button', async () => {
      // given
      props.areAllOffersSelected = true
      renderActionsBar(props)
      const deactivateButton = screen.getByText('Désactiver')
      const expectedBody = {
        isActive: false,
        nameOrIsbn: 'keyword',
        offererId: 'A4',
        venueId: 'E3',
      }

      // when
      await userEvent.click(deactivateButton)
      const confirmDeactivateButton = screen.getAllByText('Désactiver')[1]
      await userEvent.click(confirmDeactivateButton)

      // then
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
      // given
      props.areAllOffersSelected = true
      renderActionsBar(props)
      const deactivateButton = screen.getByText('Désactiver')

      // when
      await userEvent.click(deactivateButton)
      const cancelDeactivateButton = screen.getAllByText('Annuler')[1]
      await userEvent.click(cancelDeactivateButton)

      // then
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
      // given
      props.areAllOffersSelected = false
      renderActionsBar(props)
      const deactivateButton = screen.getByText('Désactiver')

      // when
      await userEvent.click(deactivateButton)
      const cancelDeactivateButton = screen.getAllByText('Annuler')[1]
      await userEvent.click(cancelDeactivateButton)

      // then
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
})
