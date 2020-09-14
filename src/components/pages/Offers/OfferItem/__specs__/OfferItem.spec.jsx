import React from 'react'
import { mount, shallow } from 'enzyme'
import { MemoryRouter } from 'react-router'
import OfferItem from '../OfferItem'
import offersMock from '../../__specs__/offersMock'

describe('src | components | pages | Offers | OfferItem', () => {
  let props
  let dispatch = jest.fn()
  let updateOffer = jest.fn()

  const activeOfferWithActiveMediation = offersMock[0]
  const activeOfferWithOutActiveMediation = offersMock[1]
  const deactivedOfferWithActiveMediation = offersMock[2]
  const activeOfferWithActiveMediationAndNotEditable = offersMock[3]
  const activeThingOfferWithActiveMediation = offersMock[4]

  beforeEach(() => {
    props = {
      aggregatedStock: {},
      dispatch,
      offer: activeOfferWithActiveMediation,
      location: {
        search: '?orderBy=offer.id+desc',
      },
      maxDate: {
        format: jest.fn(),
      },
      mediations: [{ id: 'HA', isActive: true, thumbUrl: 'https://url.to/thumb' }],
      offerTypeLabel: 'fake label',
      offerer: {},
      product: {},
      availabilityMessage: 'Encore 7 stocks restant',
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
        // given
        props.offer = activeOfferWithOutActiveMediation
        props.offer.thumbUrl = '/fake-product-url'
        props.mediations = []

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const thumbImage = wrapper.find('img').first()
        expect(thumbImage.prop('src')).toBe('/fake-product-url')
      })

      it('should render an image with an empty url when offer does not have a thumb url', () => {
        // given
        props.offer = activeOfferWithOutActiveMediation
        props.offer.thumbUrl = null
        props.mediations = []

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
          props.offer = activeOfferWithActiveMediation
          const wrapper = shallow(<OfferItem {...props} />)
          const disableButton = wrapper.find('button')

          // when
          disableButton.simulate('click')

          // then
          expect(updateOffer).toHaveBeenCalledWith(activeOfferWithActiveMediation.id, false)
        })

        it('should activate when offer is not active', () => {
          // given
          props.offer = deactivedOfferWithActiveMediation
          const wrapper = shallow(<OfferItem {...props} />)
          const disableButton = wrapper.find('button')

          // when
          disableButton.simulate('click')

          // then
          expect(updateOffer).toHaveBeenCalledWith(deactivedOfferWithActiveMediation.id, true)
        })
      })

      describe('edit offer link', () => {
        it('should be displayed when offer is editable', () => {
          // given
          props.offer = activeOfferWithActiveMediation

          // when
          const wrapper = mount(
            <MemoryRouter>
              <OfferItem {...props} />
            </MemoryRouter>
          )

          // then
          const editOfferLink = wrapper.find(
            `a[href="/offres/${activeOfferWithActiveMediation.id}/edition"]`
          )
          expect(editOfferLink).toHaveLength(1)
        })

        it('should not be displayed when offer is no editable', () => {
          // given
          props.offer = activeOfferWithActiveMediationAndNotEditable

          // when
          const wrapper = mount(
            <MemoryRouter>
              <OfferItem {...props} />
            </MemoryRouter>
          )

          // then
          const editOfferLink = wrapper.find(
            `a[href="/offres/${activeOfferWithActiveMediationAndNotEditable.id}"]`
          )
          expect(editOfferLink).toHaveLength(0)
        })
      })
    })

    describe('offer title', () => {
      it('should contain a link with the offer name and details link', () => {
        // given
        props.offer.name = 'Harry Potter vol.1'
        props.stocks = []

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const titleLink = wrapper.find(`a[href="/offres/${props.offer.id}?orderBy=offer.id+desc"]`)
        expect(titleLink).toHaveLength(1)
        expect(titleLink.prop('title')).toBe("Afficher le détail de l'offre")
        expect(titleLink.text()).toBe('Harry Potter vol.1')
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

    describe('when offer is an event product ', () => {
      it('should display the availability message', () => {
        // given
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = []
        props.availabilityMessage = 'Plus de stock restant'
        props.offer = activeOfferWithActiveMediation

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const venueName = wrapper.find({ children: 'Plus de stock restant' })
        expect(venueName).toHaveLength(1)
      })

      it('should display the correct text "2 dates" on the link redirecting to the offer management', () => {
        // given
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = [{}, {}]
        props.offer = activeOfferWithActiveMediation

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
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = [{ remainingQuantity: 'unlimited' }, { remainingQuantity: 13 }]
        props.offer = activeOfferWithActiveMediation

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
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = [{ remainingQuantity: 0 }, { remainingQuantity: 0 }]
        props.offer = activeOfferWithActiveMediation

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
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = [{ remainingQuantity: 0 }, { remainingQuantity: 'unlimited' }]
        props.offer = activeOfferWithActiveMediation

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
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = [
          { remainingQuantity: 0 },
          { remainingQuantity: 0 },
          { remainingQuantity: 12 },
        ]
        props.offer = activeOfferWithActiveMediation

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
      it('should display the availability message', () => {
        // given
        props.product = {
          offerType: { label: 'Une place de cinéma' },
        }
        props.stocks = []
        props.availabilityMessage = 'Plus de stock restant'
        props.offer = activeThingOfferWithActiveMediation

        // when
        const wrapper = mount(
          <MemoryRouter>
            <OfferItem {...props} />
          </MemoryRouter>
        )

        // then
        const venueName = wrapper.find({ children: 'Plus de stock restant' })
        expect(venueName).toHaveLength(1)
      })

      it('should display the correct text "1 prix" on the link redirecting to the offer management', () => {
        // given
        props.product = {
          offerType: { label: 'Une place de cinéma' },
        }
        props.stocks = [{}]
        props.offer = activeThingOfferWithActiveMediation

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
  })

  describe('event tracking', () => {
    it('should track deactivate offer when offer is active', () => {
      // given
      props.offer = activeThingOfferWithActiveMediation

      const wrapper = shallow(<OfferItem {...props} />)

      // when
      wrapper.instance().handleOnDeactivateClick()

      // then
      expect(props.trackDeactivateOffer).toHaveBeenCalledWith(
        activeThingOfferWithActiveMediation.id
      )
    })

    it('should track activate offer when offer is inactive', () => {
      // given
      props.offer = deactivedOfferWithActiveMediation
      const wrapper = shallow(<OfferItem {...props} />)

      // when
      wrapper.instance().handleOnDeactivateClick()

      // then
      expect(props.trackActivateOffer).toHaveBeenCalledWith(deactivedOfferWithActiveMediation.id)
    })
  })
})
