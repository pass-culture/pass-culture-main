import '@testing-library/jest-dom'
import { within } from '@testing-library/dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import OfferItem from '../OfferItem'

const renderOfferItem = props => {
  return render(
    <MemoryRouter>
      <table>
        <tbody>
          <OfferItem {...props} />
        </tbody>
      </table>
    </MemoryRouter>
  )
}

jest.mock('utils/fetch', () => {
  return {
    fetchFromApiWithCredentials: jest.fn().mockImplementation(() => Promise.resolve()),
  }
})

describe('src | components | pages | Offers | OfferItem', () => {
  let props
  let eventOffer

  beforeEach(() => {
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
      status: 'APPROVED',
    }

    props = {
      dispatch: jest.fn(),
      offer: eventOffer,
      location: {
        search: '?orderBy=offer.id+desc',
      },
      selectOffer: jest.fn(),
      stocks: [],
      venue: {
        isVirtual: false,
        name: 'Paris',
      },
      trackActivateOffer: jest.fn(),
      trackDeactivateOffer: jest.fn(),
      refreshOffers: jest.fn(),
    }
  })

  describe('render', () => {
    describe('thumb Component', () => {
      it('should render an image with url from offer when offer has a thumb url', () => {
        // when
        renderOfferItem(props)

        // then
        expect(screen.getByAltText("Miniature d'offre")).toHaveAttribute('src', eventOffer.thumbUrl)
      })

      it('should render an image with an empty url when offer does not have a thumb url', () => {
        // given
        props.offer.thumbUrl = null

        // when
        renderOfferItem(props)

        // then
        expect(screen.getByText("Miniature d'offre")).toBeInTheDocument()
      })
    })

    describe('action buttons', () => {
      it('should display a button to show offer stocks', () => {
        // given
        renderOfferItem(props)

        // then
        expect(screen.queryByText('Stocks')).toBeInTheDocument()
        expect(screen.queryByText('Stocks')).toHaveAttribute(
          'href',
          `/offres/${eventOffer.id}/stocks`
        )
      })

      describe('edit offer link', () => {
        it('should be displayed when offer is editable', () => {
          // when
          renderOfferItem(props)

          // then
          const links = screen.getAllByRole('link')
          expect(links[links.length - 1]).toHaveAttribute(
            'href',
            `/offres/${eventOffer.id}/edition`
          )
        })

        it('should not be displayed when offer is no editable', () => {
          props.offer.isEditable = false

          // when
          renderOfferItem(props)

          // then
          const links = screen.getAllByRole('link')
          expect(links[links.length - 1]).not.toHaveAttribute(
            'href',
            `/offres/${eventOffer.id}/edition`
          )
        })
      })
    })

    describe('offer title', () => {
      it('should contain a link with the offer name and details link', () => {
        // when
        renderOfferItem(props)

        // then
        const offerTitle = screen.queryByText(props.offer.name, 'a')
        expect(offerTitle).toBeInTheDocument()
        expect(offerTitle).toHaveAttribute('href', `/offres/${props.offer.id}/edition`)
        expect(offerTitle).toHaveAttribute('title', "Afficher le détail de l'offre")
      })
    })

    it('should display the venue name when venue public name is not given', () => {
      // given
      props.venue = {
        name: 'Paris',
        isVirtual: false,
      }

      // when
      renderOfferItem(props)

      // then
      expect(screen.queryByText(props.venue.name)).toBeInTheDocument()
    })

    it('should display the venue public name when is given', () => {
      // given
      props.venue = {
        name: 'Paris',
        publicName: 'lieu de ouf',
        isVirtual: false,
      }

      // when
      renderOfferItem(props)

      // then
      expect(screen.queryByText(props.venue.publicName)).toBeInTheDocument()
    })

    it('should display the offerer name with "- Offre numérique" when venue is virtual', () => {
      // given
      props.venue = {
        isVirtual: true,
        name: 'Gaumont Montparnasse',
        offererName: 'Gaumont',
        publicName: 'Gaumontparnasse',
      }

      // when
      renderOfferItem(props)

      // then
      expect(screen.queryByText('Gaumont - Offre numérique')).toBeInTheDocument()
    })

    describe('offer remaining quantity', () => {
      it('should be 0 when offer has no stock', () => {
        // when
        renderOfferItem(props)

        // then
        expect(screen.queryByText('0')).toBeInTheDocument()
      })

      it('should be the sum of offer stocks remaining quantity', () => {
        // given
        props.stocks = [
          { remainingQuantity: 0 },
          { remainingQuantity: 2 },
          { remainingQuantity: 3 },
        ]

        // when
        renderOfferItem(props)

        // then
        expect(screen.queryByText('5')).toBeInTheDocument()
      })

      it('should be "illimité" when at least one stock is unlimited', () => {
        // given
        props.stocks = [{ remainingQuantity: 0 }, { remainingQuantity: 'unlimited' }]

        // when
        renderOfferItem(props)

        // then
        expect(screen.queryByText('Illimité')).toBeInTheDocument()
      })
    })

    describe('when offer is an event product', () => {
      it('should display the correct text "2 dates"', () => {
        // given
        props.stocks = [{ remainingQuantity: 'unlimited' }, { remainingQuantity: 'unlimited' }]

        // when
        renderOfferItem(props)

        // then
        expect(screen.queryByText('2 dates')).toBeInTheDocument()
      })

      it('should not display a warning when no stocks are sold out', () => {
        // given
        props.stocks = [{ remainingQuantity: 'unlimited' }, { remainingQuantity: 13 }]

        // when
        renderOfferItem(props)

        // then
        const numberOfStocks = screen.getByText('2 dates').closest('span')
        expect(within(numberOfStocks).queryByRole('img')).not.toBeInTheDocument()
      })

      it('should not display a warning when all stocks are sold out', () => {
        // given
        props.stocks = [{ remainingQuantity: 0 }, { remainingQuantity: 0 }]

        // when
        renderOfferItem(props)

        // then
        const numberOfStocks = screen.getByText('2 dates').closest('span')
        expect(within(numberOfStocks).queryByRole('img')).not.toBeInTheDocument()
      })

      it('should display a warning with number of stocks sold out when at least one stock is sold out', () => {
        // given
        props.stocks = [
          { remainingQuantity: 0, hasBookingLimitDatetimePassed: false },
          { remainingQuantity: 'unlimited', hasBookingLimitDatetimePassed: false },
        ]

        // when
        renderOfferItem(props)

        // then
        const numberOfStocks = screen.getByText('2 dates').closest('span')
        expect(within(numberOfStocks).queryAllByRole('img')[0]).toHaveAttribute(
          'src',
          expect.stringContaining('ico-warning-stocks')
        )
        expect(within(numberOfStocks).queryByText('1 date épuisée')).toBeInTheDocument()
      })

      it('should pluralize number of stocks sold out when at least two stocks are sold out', () => {
        // given
        props.stocks = [
          { remainingQuantity: 0, hasBookingLimitDatetimePassed: false },
          { remainingQuantity: 0, hasBookingLimitDatetimePassed: false },
          { remainingQuantity: 12, hasBookingLimitDatetimePassed: false },
        ]

        // when
        renderOfferItem(props)

        // then
        const numberOfStocks = screen.getByText('3 dates').closest('span')
        expect(within(numberOfStocks).queryByText('2 dates épuisées')).toBeInTheDocument()
      })
    })
  })
})
