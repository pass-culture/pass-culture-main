import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import type { Store } from 'redux'

import { OfferStatus } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import * as useAnalytics from 'hooks/useAnalytics'
import { configureTestStore } from 'store/testUtils'

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

const renderOfferItem = (props: OfferItemProps, store: Store) => {
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <table>
          <tbody>
            <OfferItem {...props} />
          </tbody>
        </table>
      </MemoryRouter>
    </Provider>
  )
}

describe('src | components | pages | Offers | OfferItem', () => {
  let props: OfferItemProps
  let eventOffer: Offer
  let store: Store

  beforeEach(() => {
    store = configureTestStore({})

    eventOffer = {
      id: 'M4',
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
      renderOfferItem(props, store)

      // then
      await userEvent.click(
        screen.getAllByRole('img', { name: /éditer l'offre/ })[0]
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
          offerId: 'M4',
        }
      )
    })

    it('should track when clicking on offer stocks', async () => {
      // given
      renderOfferItem(props, store)
      await userEvent.click(screen.getByText('Stocks'))

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
          offerId: 'M4',
        }
      )
    })

    it('should track when clicking on offer pen', async () => {
      // when
      renderOfferItem(props, store)
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
          offerId: 'M4',
        }
      )
    })
  })

  it('should track when clicking on offer title', async () => {
    // when
    renderOfferItem(props, store)

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
        offerId: 'M4',
      }
    )
  })

  describe('draft offers', () => {
    it('should track with draft informations', async () => {
      // when
      props.offer.status = OfferStatus.DRAFT
      renderOfferItem(props, store)

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
          to: 'details',
          used: 'OffersTitle',
          offerId: 'M4',
        }
      )
    })

    it('should track with draft informations', async () => {
      // when
      props.offer.status = OfferStatus.DRAFT
      renderOfferItem(props, store)

      // then
      const deleteDraftOfferButton = screen.getByRole('button', {
        name: 'Supprimer le brouillon',
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
          offerId: 'M4',
          isDraft: true,
        }
      )
    })
  })
})
