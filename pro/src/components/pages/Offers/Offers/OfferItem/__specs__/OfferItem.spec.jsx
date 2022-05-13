import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import { MemoryRouter } from 'react-router'
import OfferItem from '../OfferItem'
import { Provider } from 'react-redux'
import React from 'react'
import { configureTestStore } from 'store/testUtils'
import { within } from '@testing-library/dom'

const renderOfferItem = (props, store) => {
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
  let props
  let eventOffer
  let store

  beforeEach(() => {
    store = configureTestStore({})

    eventOffer = {
      id: 'M4',
      isActive: true,
      isEditable: true,
      isFullyBooked: false,
      isEvent: true,
      isThing: false,
      hasBookingLimitDatetimesPassed: false,
      name: 'My little offer',
      thumbUrl: '/my-fake-thumb',
      status: 'ACTIVE',
      stocks: [],
      venue: {
        isVirtual: false,
        name: 'Paris',
        departementCode: '973',
      },
    }

    props = {
      dispatch: jest.fn(),
      offer: eventOffer,
      location: {
        search: '?orderBy=offer.id+desc',
      },
      selectOffer: jest.fn(),
      trackActivateOffer: jest.fn(),
      trackDeactivateOffer: jest.fn(),
      refreshOffers: jest.fn(),
    }
  })

  describe('render', () => {
    describe('thumb Component', () => {
      it('should render an image with url from offer when offer has a thumb url', () => {
        // when
        renderOfferItem(props, store)

        // then
        expect(
          screen.getAllByRole('img', { name: /éditer l'offre/ })[0]
        ).toHaveAttribute('src', eventOffer.thumbUrl)
      })

      it('should render an image with an empty url when offer does not have a thumb url', () => {
        // given
        props.offer.thumbUrl = null

        // when
        renderOfferItem(props, store)

        // then
        expect(
          screen.getAllByRole('img', { name: /éditer l'offre/ })[0]
        ).toHaveAttribute('src')
      })
    })

    describe('action buttons', () => {
      it('should display a button to show offer stocks', () => {
        // given
        renderOfferItem(props, store)

        // then
        expect(screen.queryByText('Stocks')).toBeInTheDocument()
        expect(screen.queryByText('Stocks')).toHaveAttribute(
          'href',
          `/offre/${eventOffer.id}/individuel/stocks`
        )
      })

      describe('edit offer link', () => {
        it('should be displayed when offer is editable', () => {
          // when
          renderOfferItem(props, store)

          // then
          const links = screen.getAllByRole('link')
          expect(links[links.length - 1]).toHaveAttribute(
            'href',
            `/offre/${eventOffer.id}/individuel/edition`
          )
        })

        it('should not be displayed when offer is no editable', () => {
          props.offer.isEditable = false

          // when
          renderOfferItem(props, store)

          // then
          const links = screen.getAllByRole('link')
          expect(links[links.length - 1]).not.toHaveAttribute(
            'href',
            `/offre/${eventOffer.id}/individuel/edition`
          )
        })
      })
    })

    describe('offer title', () => {
      it('should contain a link with the offer name and details link', () => {
        // when
        renderOfferItem(props, store)

        // then
        const offerTitle = screen.queryByText(props.offer.name, 'a')
        expect(offerTitle).toBeInTheDocument()
        expect(offerTitle).toHaveAttribute(
          'href',
          `/offre/${props.offer.id}/individuel/edition`
        )
      })
    })

    it('should display the venue name when venue public name is not given', () => {
      // given
      props.offer.venue = {
        name: 'Paris',
        isVirtual: false,
      }

      // when
      renderOfferItem(props, store)

      // then
      expect(screen.queryByText(props.offer.venue.name)).toBeInTheDocument()
    })

    it('should display the venue public name when is given', () => {
      // given
      props.offer.venue = {
        name: 'Paris',
        publicName: 'lieu de ouf',
        isVirtual: false,
      }

      // when
      renderOfferItem(props, store)

      // then
      expect(
        screen.queryByText(props.offer.venue.publicName)
      ).toBeInTheDocument()
    })

    it('should display the offerer name with "- Offre numérique" when venue is virtual', () => {
      // given
      props.offer.venue = {
        isVirtual: true,
        name: 'Gaumont Montparnasse',
        offererName: 'Gaumont',
        publicName: 'Gaumontparnasse',
      }

      // when
      renderOfferItem(props, store)

      // then
      expect(
        screen.queryByText('Gaumont - Offre numérique')
      ).toBeInTheDocument()
    })

    it('should display the isbn when given', () => {
      // given
      eventOffer.productIsbn = '123456789'

      // when
      renderOfferItem(props, store)

      // then
      expect(screen.queryByText('123456789')).toBeInTheDocument()
    })

    it('should display educational tag when offer is educational', () => {
      // given
      eventOffer.isEducational = true

      // when
      renderOfferItem(props, store)

      // then
      expect(screen.getByText('Offre collective')).toBeInTheDocument()
    })

    describe('offer remaining quantity', () => {
      it('should be 0 when offer has no stock', () => {
        // when
        renderOfferItem(props, store)

        // then
        expect(screen.queryByText('0')).toBeInTheDocument()
      })

      it('should be the sum of offer stocks remaining quantity', () => {
        // given
        props.offer.stocks = [
          { remainingQuantity: 0 },
          { remainingQuantity: 2 },
          { remainingQuantity: 3 },
        ]

        // when
        renderOfferItem(props, store)

        // then
        expect(screen.queryByText('5')).toBeInTheDocument()
      })

      it('should be "illimité" when at least one stock is unlimited', () => {
        // given
        props.offer.stocks = [
          { remainingQuantity: 0 },
          { remainingQuantity: 'unlimited' },
        ]

        // when
        renderOfferItem(props, store)

        // then
        expect(screen.queryByText('Illimité')).toBeInTheDocument()
      })
    })

    describe('when offer is an event product', () => {
      it('should display the correct text "2 dates"', () => {
        // given
        props.offer.stocks = [
          { remainingQuantity: 'unlimited' },
          { remainingQuantity: 'unlimited' },
        ]

        // when
        renderOfferItem(props, store)

        // then
        expect(screen.queryByText('2 dates')).toBeInTheDocument()
      })

      it('should display the beginning date time when only one date', () => {
        // given
        props.offer.stocks = [
          { beginningDatetime: '2021-05-27T20:00:00Z', remainingQuantity: 10 },
        ]

        // when
        renderOfferItem(props, store)

        // then
        expect(screen.getByText('27/05/2021 17:00')).toBeInTheDocument()
      })

      it('should not display a warning when no stocks are sold out', () => {
        // given
        props.offer.stocks = [
          { remainingQuantity: 'unlimited' },
          { remainingQuantity: 13 },
        ]

        // when
        renderOfferItem(props, store)

        // then
        const numberOfStocks = screen.getByText('2 dates').closest('span')
        expect(
          within(numberOfStocks).queryByRole('img')
        ).not.toBeInTheDocument()
      })

      it('should not display a warning when all stocks are sold out', () => {
        // given
        props.offer.stocks = [
          { remainingQuantity: 0 },
          { remainingQuantity: 0 },
        ]
        eventOffer.status = 'SOLD_OUT'

        // when
        renderOfferItem(props, store)

        // then
        const numberOfStocks = screen.getByText('2 dates').closest('span')
        expect(
          within(numberOfStocks).queryByRole('img')
        ).not.toBeInTheDocument()
      })

      it('should display a warning with number of stocks sold out when at least one stock is sold out', () => {
        // given
        props.offer.stocks = [
          { remainingQuantity: 0, hasBookingLimitDatetimePassed: false },
          {
            remainingQuantity: 'unlimited',
            hasBookingLimitDatetimePassed: false,
          },
        ]

        // when
        renderOfferItem(props, store)

        // then
        const numberOfStocks = screen.getByText('2 dates').closest('span')
        expect(within(numberOfStocks).queryAllByRole('img')[0]).toHaveAttribute(
          'src',
          expect.stringContaining('ico-warning-stocks')
        )
        expect(
          within(numberOfStocks).queryByText('1 date épuisée')
        ).toBeInTheDocument()
      })

      it('should pluralize number of stocks sold out when at least two stocks are sold out', () => {
        // given
        props.offer.stocks = [
          { remainingQuantity: 0, hasBookingLimitDatetimePassed: false },
          { remainingQuantity: 0, hasBookingLimitDatetimePassed: false },
          { remainingQuantity: 12, hasBookingLimitDatetimePassed: false },
        ]

        // when
        renderOfferItem(props, store)

        // then
        const numberOfStocks = screen.getByText('3 dates').closest('span')
        expect(
          within(numberOfStocks).queryByText('2 dates épuisées')
        ).toBeInTheDocument()
      })
    })

    it('should display the offer greyed when offer has pending status', () => {
      // Given
      props.offer.status = 'PENDING'

      // When
      renderOfferItem(props, store)

      // Then
      expect(screen.getByText('My little offer').closest('tr')).toHaveClass(
        'inactive'
      )
    })

    it('should display the offer greyed when offer has rejected status', () => {
      // Given
      props.offer.status = 'REJECTED'

      // When
      renderOfferItem(props, store)

      // Then
      expect(screen.getByText('My little offer').closest('tr')).toHaveClass(
        'inactive'
      )
    })

    it('should display the offer greyed when offer is inactive', () => {
      // Given
      props.offer.isActive = false

      // When
      renderOfferItem(props, store)

      // Then
      expect(screen.getByText('My little offer').closest('tr')).toHaveClass(
        'inactive'
      )
    })

    it('should not display the offer greyed when offer is active', () => {
      // Given
      props.offer.status = 'ACTIVE'

      // When
      renderOfferItem(props, store)

      // Then
      expect(screen.getByText('My little offer').closest('tr')).not.toHaveClass(
        'inactive'
      )
    })
  })
})
