import React from 'react'
import { mount } from 'enzyme'
import { MemoryRouter } from 'react-router'
import OfferItem from '../OfferItem'

describe('src | components | pages | Offers | OfferItem', () => {
  let props
  let dispatch = jest.fn()
  let updateOffer = jest.fn()

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
    }

    props = {
      dispatch,
      offer: eventOffer,
      location: {
        search: '?orderBy=offer.id+desc',
      },
      stocks: [],
      venue: {
        name: 'Paris',
      },
      trackActivateOffer: jest.fn(),
      trackDeactivateOffer: jest.fn(),
      updateOffer,
    }
  })

  describe('render', () => {
    describe('thumb Component', () => {
      it('should render an image with url from offer when offer has a thumb url', () => {
        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const thumbImage = wrapper.find('img').first()
        expect(thumbImage.prop('src')).toBe(eventOffer.thumbUrl)
      })

      it('should render an image with an empty url when offer does not have a thumb url', () => {
        // given
        eventOffer.thumbUrl = null

        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )
        // when
        const thumbDefaultImage = wrapper.find('svg')

        // then
        expect(thumbDefaultImage).toHaveLength(1)
      })
    })

    describe('action buttons', () => {
      describe('switch activate', () => {
        it('should deactivate when offer is active', () => {
          // given
          const wrapper = mount(
            <MemoryRouter>
              <OfferItem {...props} />
            </MemoryRouter>
          )
          const disableButton = wrapper.find('button')

          // when
          disableButton.invoke('onClick')()

          // then
          expect(updateOffer).toHaveBeenCalledWith(eventOffer.id, false)
        })

        it('should activate when offer is not active', () => {
          // given
          eventOffer.isActive = false
          const wrapper = mount(
            <MemoryRouter>
              <OfferItem {...props} />
            </MemoryRouter>
          )
          const disableButton = wrapper.find('button')

          // when
          disableButton.invoke('onClick')()

          // then
          expect(updateOffer).toHaveBeenCalledWith(eventOffer.id, true)
        })
      })

      describe('edit offer link', () => {
        it('should be displayed when offer is editable', () => {
          // when
          const wrapper = mount(
            <MemoryRouter>
              <OfferItem {...props} />
            </MemoryRouter>
          )

          // then
          const editOfferLink = wrapper.find(`a[href="/offres/${eventOffer.id}/edition"]`)
          expect(editOfferLink).toHaveLength(1)
        })

        it('should not be displayed when offer is no editable', () => {
          props.offer.isEditable = false

          // when
          const wrapper = mount(
            <MemoryRouter>
              <OfferItem {...props} />
            </MemoryRouter>
          )

          // then
          const editOfferLink = wrapper.find(`a[href="/offres/${props.offer.id}/edition"]`)
          expect(editOfferLink).toHaveLength(0)
        })
      })
    })

    describe('offer title', () => {
      it('should contain a link with the offer name and details link', () => {
        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const titleLink = wrapper.find(`a[href="/offres/${props.offer.id}"]`)
        expect(titleLink).toHaveLength(1)
        expect(titleLink.prop('title')).toBe("Afficher le détail de l'offre")
        expect(titleLink.text()).toBe(eventOffer.name)
      })
    })

    it('should display the venue name when venue public name is not given', () => {
      // given
      props.venue = {
        name: 'Paris',
      }

      // when
      const wrapper = mount(
        <MemoryRouter>
          <OfferItem {...props} />
        </MemoryRouter>
      )

      // then
      const venueName = wrapper.find({ children: 'Paris' })
      expect(venueName).toHaveLength(1)
    })

    it('should display the venue public name when is given', () => {
      // given
      props.venue = {
        name: 'Paris',
        publicName: 'lieu de ouf',
      }

      // when
      const wrapper = mount(
        <MemoryRouter>
          <OfferItem {...props} />
        </MemoryRouter>
      )

      // then
      const venueName = wrapper.find({ children: 'lieu de ouf' })
      expect(venueName).toHaveLength(1)
    })

    describe('offer remaining quantity', () => {
      it('should be 0 when offer has no stock', () => {
        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const remainingQuantity = wrapper.find({ children: 0 })
        expect(remainingQuantity).toHaveLength(1)
      })

      it('should be the sum of offer stocks remaining quantity', () => {
        // given
        props.stocks = [
          { remainingQuantity: 0 },
          { remainingQuantity: 2 },
          { remainingQuantity: 3 },
        ]

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const remainingQuantity = wrapper.find({ children: 5 })
        expect(remainingQuantity).toHaveLength(1)
      })

      it('should be "illimité" when at least one stock is unlimited', () => {
        // given
        props.stocks = [{ remainingQuantity: 0 }, { remainingQuantity: 'unlimited' }]

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const remainingQuantity = wrapper.find({ children: 'Illimité' })
        expect(remainingQuantity).toHaveLength(1)
      })
    })

    describe('when offer is an event product', () => {
      it('should display the correct text "2 dates" on the link redirecting to the offer management', () => {
        // given
        props.stocks = [{ remainingQuantity: 'unlimited' }, { remainingQuantity: 'unlimited' }]

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const stockLink = wrapper.find(`a[href="/offres/${props.offer.id}?gestion"]`)
        expect(stockLink.text()).toBe('2 dates')
      })

      it('should not display a warning when no stocks are sold out', () => {
        // given
        props.stocks = [{ remainingQuantity: 'unlimited' }, { remainingQuantity: 13 }]

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const numberOfStocksDescription = wrapper
          .find(`a[href="/offres/${props.offer.id}?gestion"]`)
          .parent()
        expect(numberOfStocksDescription.find('img')).toHaveLength(0)
      })

      it('should not display a warning when all stocks are sold out', () => {
        // given
        props.stocks = [{ remainingQuantity: 0 }, { remainingQuantity: 0 }]

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const numberOfStocksDescription = wrapper
          .find(`a[href="/offres/${props.offer.id}?gestion"]`)
          .parent()
        expect(numberOfStocksDescription.find('img')).toHaveLength(0)
      })

      it('should display a warning with number of stocks sold out when at least one stock is sold out', () => {
        // given
        props.stocks = [{ remainingQuantity: 0 }, { remainingQuantity: 'unlimited' }]

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const numberOfStocksWrapper = wrapper
          .find(`a[href="/offres/${props.offer.id}?gestion"]`)
          .parents()
          .at(1)

        const numberOfStocksDescription = numberOfStocksWrapper
          .findWhere(node => node.text() === '1 date épuisée')
          .first()

        expect(numberOfStocksWrapper.find('img')).toHaveLength(2)
        expect(numberOfStocksDescription).toHaveLength(1)
      })

      it('should pluralize number of stocks sold out when at least two stocks are sold out', () => {
        // given
        props.stocks = [
          { remainingQuantity: 0 },
          { remainingQuantity: 0 },
          { remainingQuantity: 12 },
        ]

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const numberOfStocksDescription = wrapper
          .findWhere(node => node.text() === '2 dates épuisées')
          .first()

        expect(numberOfStocksDescription).toHaveLength(1)
      })
    })

    describe('when offer is a thing product', () => {
      let thingOffer
      beforeEach(() => {
        thingOffer = Object.assign(eventOffer, { isThing: true, isOffer: false })
        props.offer = thingOffer
      })

      it('should display the correct text "1 prix" on the link redirecting to the offer management', () => {
        // given
        props.stocks = [{ remainingQuantity: 'unlimited' }]

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const stockLink = wrapper.find(`a[href="/offres/${props.offer.id}?gestion"]`)
        expect(stockLink.text()).toBe('1 prix')
      })
    })

    it('should display the offer status based on offer and stocks props', () => {
      // given
      props.stocks = [{ remainingQuantity: 0 }]

      // when
      const wrapper = mount(
        <MemoryRouter>
          <OfferItem {...props} />
        </MemoryRouter>
      )

      // then
      const soldOutOfferStatus = wrapper.findWhere(node => node.text() === 'épuisée').first()
      expect(soldOutOfferStatus).toHaveLength(1)
    })
  })

  describe('event tracking', () => {
    it('should track deactivate offer when offer is active', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <OfferItem {...props} />
        </MemoryRouter>
      )
      // when
      const deactivateOfferButton = wrapper.find({ children: 'Désactiver' })
      deactivateOfferButton.invoke('onClick')()

      // then
      expect(props.trackDeactivateOffer).toHaveBeenCalledWith(eventOffer.id)
    })

    it('should track activate offer when offer is inactive', () => {
      // given
      eventOffer.isActive = false

      const wrapper = mount(
        <MemoryRouter>
          <OfferItem {...props} />
        </MemoryRouter>
      )
      // when
      const activateOfferButton = wrapper.find({ children: 'Activer' })
      activateOfferButton.invoke('onClick')()

      // then
      expect(props.trackActivateOffer).toHaveBeenCalledWith(eventOffer.id)
    })
  })
})
