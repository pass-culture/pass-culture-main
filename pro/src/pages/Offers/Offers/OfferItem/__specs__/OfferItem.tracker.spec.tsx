import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferItem, { OfferItemProps } from '../OfferItem'

const mockLogEvent = jest.fn()
jest.mock('apiClient/api', () => ({
  api: {
    deleteDraftOffers: jest.fn().mockResolvedValue({
      isOk: true,
      message: 'youpi draft deleted !',
      payload: null,
    }),
  },
}))

const renderOfferItem = (props: OfferItemProps) =>
  renderWithProviders(
    <table>
      <tbody>
        <OfferItem {...props} />
      </tbody>
    </table>
  )

describe('src | components | pages | Offers | OfferItem', () => {
  let props: OfferItemProps
  let eventOffer: Offer
  const offerId = 1

  beforeEach(() => {
    eventOffer = {
      nonHumanizedId: offerId,
      isActive: true,
      isEditable: true,
      isEvent: true,
      hasBookingLimitDatetimesPassed: false,
      name: 'My little offer',
      thumbUrl: '/my-fake-thumb',
      status: OfferStatus.ACTIVE,
      stocks: [],
      venue: {
        isVirtual: false,
        name: 'Paris',
        departementCode: '973',
        offererName: 'Offerer name',
      },
      isEducational: false,
    }

    props = {
      refreshOffers: jest.fn(),
      offer: eventOffer,
      selectOffer: jest.fn(),
      audience: Audience.INDIVIDUAL,
    }

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  describe('offer item tracking', () => {
    it('track when clicking on offer thumb', async () => {
      // when
      renderOfferItem(props)

      // then
      await userEvent.click(
        screen.getAllByRole('img', { name: /éditer l’offre/ })[0]
      )
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'Offers',
          isEdition: true,
          isDraft: false,
          to: 'recapitulatif',
          used: 'OffersThumb',
          offerId: offerId,
        }
      )
    })

    it('should track when clicking on offer stocks', async () => {
      // given
      renderOfferItem(props)
      await userEvent.click(
        screen.getByRole('link', { name: 'Dates et capacités' })
      )

      // then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'Offers',
          isEdition: true,
          isDraft: false,
          to: 'stocks',
          used: 'OffersStocks',
          offerId: offerId,
        }
      )
    })

    it('should track when clicking on offer pen', async () => {
      // when
      renderOfferItem(props)
      // then
      const editLink = screen.getAllByRole('link')
      await userEvent.click(editLink[3])
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'Offers',
          isEdition: true,
          isDraft: false,
          to: 'recapitulatif',
          used: 'OffersPen',
          offerId: offerId,
        }
      )
    })
  })

  it('should track when clicking on offer title', async () => {
    // when
    renderOfferItem(props)

    // then
    const offerTitle = screen.getByText(props.offer.name as string, {
      selector: 'a',
    })
    await userEvent.click(offerTitle)
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'Offers',
        isEdition: true,
        isDraft: false,
        to: 'recapitulatif',
        used: 'OffersTitle',
        offerId: offerId,
      }
    )
  })

  describe('draft offers', () => {
    it('should track with draft informations', async () => {
      // when
      props.offer.status = OfferStatus.DRAFT
      renderOfferItem(props)

      // then
      const offerTitle = screen.getByText(props.offer.name as string, {
        selector: 'a',
      })
      await userEvent.click(offerTitle)
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'Offers',
          isEdition: true,
          isDraft: true,
          to: 'informations',
          used: 'OffersTitle',
          offerId: offerId,
        }
      )
    })

    it('should track with draft informations', async () => {
      // when
      props.offer.status = OfferStatus.DRAFT
      renderOfferItem(props)

      // then
      const deleteDraftOfferButton = screen.getByRole('button', {
        name: 'Supprimer',
      })
      await userEvent.click(deleteDraftOfferButton)
      const confirmDeleteButton = screen.getByRole('button', {
        name: 'Supprimer ce brouillon',
      })
      await userEvent.click(confirmDeleteButton)
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.DELETE_DRAFT_OFFER,
        {
          from: 'Offers',
          used: 'OffersTrashicon',
          offerId: offerId,
          isDraft: true,
        }
      )
    })
  })
})
