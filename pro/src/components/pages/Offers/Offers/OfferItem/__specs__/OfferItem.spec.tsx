import '@testing-library/jest-dom'

import { within } from '@testing-library/dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import type { Store } from 'redux'

import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import { configureTestStore } from 'store/testUtils'

import OfferItem, { OfferItemProps } from '../OfferItem'

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
        const offerTitle = screen.queryByText(props.offer.name as string, {
          selector: 'a',
        })
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
        offererName: 'Offerer name',
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
        offererName: 'Offerer name',
      }

      // when
      renderOfferItem(props, store)

      // then
      expect(screen.queryByText('lieu de ouf')).toBeInTheDocument()
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

    describe('offer remaining quantity or institution', () => {
      it('should be 0 when individual offer has no stock', () => {
        // when
        renderOfferItem(props, store)

        // then
        expect(screen.queryByText('0')).toBeInTheDocument()
      })

      it('should be the sum of individual offer stocks remaining quantity', () => {
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

      it('should be "illimité" when at least one stock of the individual offer is unlimited', () => {
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

      it('should display "Tous les établissements" when offer is collective and is not assigned to a specific institution', () => {
        // given
        props.audience = Audience.COLLECTIVE
        props.offer.educationalInstitution = null

        // when
        renderOfferItem(props, store)

        // then
        expect(
          screen.queryByText('Tous les établissements')
        ).toBeInTheDocument()
      })

      it('should display "Tous les établissements" when offer is collective and is assigned to a specific institution', () => {
        // given
        props.audience = Audience.COLLECTIVE
        props.offer.educationalInstitution = {
          id: 1,
          name: 'Collège Bellevue',
          city: 'Alès',
          postalCode: '30100',
        }

        // when
        renderOfferItem(props, store)

        // then
        expect(screen.queryByText('Collège Bellevue')).toBeInTheDocument()
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
          {
            beginningDatetime: new Date('2021-05-27T20:00:00Z'),
            remainingQuantity: 10,
          },
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
        expect(screen.queryByText(/épuisée/)).not.toBeInTheDocument()
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
        expect(screen.queryByText(/épuisées/)).not.toBeInTheDocument()
      })

      it('should display a warning with number of stocks sold out when at least one stock is sold out', () => {
        // given
        props.offer.stocks = [
          { remainingQuantity: 0 },
          {
            remainingQuantity: 'unlimited',
          },
        ]

        // when
        renderOfferItem(props, store)

        // then
        const numberOfStocks = screen.getByText('1 date épuisée', {
          selector: 'span',
        })
        expect(within(numberOfStocks).queryByRole('img')).toHaveAttribute(
          'src',
          expect.stringContaining('ico-warning-stocks')
        )
      })

      it('should pluralize number of stocks sold out when at least two stocks are sold out', () => {
        // given
        props.offer.stocks = [
          { remainingQuantity: 0 },
          { remainingQuantity: 0 },
          { remainingQuantity: 12 },
        ]

        // when
        renderOfferItem(props, store)

        // then
        expect(
          screen.queryByText('2 dates épuisées', { selector: 'span' })
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
