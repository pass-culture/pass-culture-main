import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import type { Store } from 'redux'

import * as useAnalytics from 'components/hooks/useAnalytics'
import { Events } from 'core/FirebaseEvents/constants'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import { configureTestStore } from 'store/testUtils'

import OfferItem, { OfferItemProps } from '../OfferItem'

const mockLogEvent = jest.fn()

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
      status: 'ACTIVE',
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
        await screen.getAllByRole('img', { name: /éditer l'offre/ })[0]
      )
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'Offers',
          isEdition: true,
          to: 'recapitulatif',
          used: 'OffersThumb',
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
          to: 'stocks',
          used: 'OffersStocks',
        }
      )
    })

    it('should track when clicking on offer pen', async () => {
      // when
      renderOfferItem(props, store)

      // then
      const links = screen.getAllByRole('link')
      const editLink = links[links.length - 1]
      await userEvent.click(editLink)
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'Offers',
          isEdition: true,
          to: 'recapitulatif',
          used: 'OffersPen',
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
        to: 'recapitulatif',
        used: 'OffersTitle',
      }
    )
  })
})
