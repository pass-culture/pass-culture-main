import React from 'react'
import { mount, shallow } from 'enzyme'
import offersMock from '../../tests/offersMock'
import { Icon } from 'pass-culture-shared'

import { NavLink } from 'react-router-dom'
import Dotdotdot from 'react-dotdotdot'
import Thumb from 'components/layout/Thumb'

import OfferItem from '../OfferItem'

describe('src | components | pages | Offers | OfferItem', () => {
  let dispatch = jest.fn()
  let props

  beforeEach(() => {
    props = {
      dispatch: dispatch,
      offer: offersMock[0],
      mediations: [{id: 'HA', isActive: true, thumbUrl: 'https://url.to/thumb'}],
      location: {
        search: '?orderBy=offer.id+desc',
      },
      venue: {
        name: 'Paris',
      },
      stocks: [],
    }
  })

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<OfferItem {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('click on "disable" button', () => {
    it('should dispatch an action with the correct payload', () => {
      // given
      const wrapper = shallow(<OfferItem {...props} />)
      const disableButton = wrapper.find('button')
      const expectedParams = {
        config: {
          apiPath: '/offers/M4',
          body: { isActive: false },
          isMergingDatum: true,
          isMutaginArray: false,
          isMutatingDatum: true,
          method: 'PATCH',
          normalizer: {
            mediations: 'mediations',
            product: { normalizer: { offers: 'offers' }, stateKey: 'products' },
            stocks: 'stocks',
            venue: {
              normalizer: { managingOfferer: 'offerers' },
              stateKey: 'venues',
            },
          },
        },
        type: 'REQUEST_DATA_PATCH_/OFFERS/M4',
      }

      // when
      disableButton.simulate('click')

      // then
      expect(dispatch.mock.calls[0][0]).toEqual(expectedParams)
    })
  })

  describe('render offer item', () => {
    describe('Thumb Component', () => {
      it('should render a Thumb Component with the given url when offer has an active mediation', () => {
        // given
        props.offer.activeMediation = {'thumbUrl': 'https://url.to/thumb'}

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const thumbComponent = wrapper.find(Thumb)
        expect(thumbComponent).toBeDefined()
        expect(thumbComponent.prop('alt')).toBe('offre')
        expect(thumbComponent.prop('src')).toBe('https://url.to/thumb')
      })

      it('should render a Thumb Component with an empty url when offer does not have an active mediation', () => {
        // given
        props.offer = offersMock[1]
        props.mediations = []

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const thumbComponent = wrapper.find(Thumb)
        expect(thumbComponent).toBeDefined()
        expect(thumbComponent.prop('alt')).toBe('offre')
        expect(thumbComponent.prop('src')).toBe('')
      })
    })

    it('should contain a Navlink Component with the right props and containing a DotDotDot component', () => {
      // given
      props.product = {
        name: 'fake name',
      }
      props.stocks = []

      // when
      const wrapper = shallow(<OfferItem {...props} />)

      // then
      const navLinkComponent = wrapper.find(NavLink).first()
      expect(navLinkComponent).toBeDefined()
      expect(navLinkComponent.prop('className')).toBe('name')
      expect(navLinkComponent.prop('to')).toBe(
        '/offres/M4?orderBy=offer.id+desc'
      )
      expect(navLinkComponent.prop('title')).toBe('fake name')
      const dotdotdotComponent = navLinkComponent.find(Dotdotdot)
      expect(dotdotdotComponent).toBeDefined()
      expect(dotdotdotComponent.prop('clamp')).toBe(1)
      expect(dotdotdotComponent.html()).toBe('<div>fake name</div>')
    })

    it('should display informations of the type of offer, the offerer and the venue name when venue public name is not given', () => {
      // given
      props.offerTypeLabel = 'a thing'
      props.offerer = {
        name: 'UGC',
      }
      props.venue = {
        name: 'Paris',
      }

      // when
      const wrapper = shallow(<OfferItem {...props} />)

      // then
      const offerInfosElement = wrapper.find('ul.infos').first()
      const infosSubItems = offerInfosElement.find('li')
      expect(infosSubItems).toHaveLength(3)

      expect(infosSubItems.at(0).prop('className')).toBe('is-uppercase')
      expect(infosSubItems.at(0).text()).toBe('a thing')
      expect(infosSubItems.at(1).text()).toEqual('Structure : UGC')
      expect(infosSubItems.at(2).text()).toEqual('Lieu : Paris')
    })

    it('should display informations of the type of offer, the offerer and the venue public name when is given', () => {
      // given
      props.offerTypeLabel = 'a thing'
      props.offerer = {
        name: 'UGC',
      }
      props.venue = {
        name: 'Paris',
        publicName: 'lieu de ouf',
      }

      // when
      const wrapper = shallow(<OfferItem {...props} />)

      // then
      const offerInfosElement = wrapper.find('ul.infos').first()
      const infosSubItems = offerInfosElement.find('li')
      expect(infosSubItems).toHaveLength(3)

      expect(infosSubItems.at(0).prop('className')).toBe('is-uppercase')
      expect(infosSubItems.at(0).text()).toBe('a thing')
      expect(infosSubItems.at(1).text()).toBe('Structure : UGC')
      expect(infosSubItems.at(2).text()).toBe('Lieu : lieu de ouf')
    })

    it('should display the number of participants eligible to the offer and user picto when 1 participant', () => {
      // given
      props.aggregatedStock = {
        available: 0,
        groupSizeMin: 1,
        groupSizeMax: 5,
        priceMin: 0,
        priceMax: 0,
      }

      // when
      const wrapper = shallow(<OfferItem {...props} />)

      // then
      const offerInfosElement = wrapper.find('ul.infos').at(1)
      const offerInfosSubElements = offerInfosElement.find('li')
      expect(offerInfosSubElements.at(0).prop('title')).toBe(
        'entre 1 et 5 personnes'
      )

      const userPictoComponent = offerInfosSubElements.at(0).find(Icon)
      expect(userPictoComponent).toBeDefined()
      expect(userPictoComponent.prop('svg')).toBe('picto-user')
    })

    it('should display the number of participants eligible to the offer and group picto when more than 1 participants', () => {
      // given
      props.aggregatedStock = {
        available: 0,
        groupSizeMin: 2,
        groupSizeMax: 5,
        priceMin: 0,
        priceMax: 0,
      }

      // when
      const wrapper = shallow(<OfferItem {...props} />)

      // then
      const offerInfosElement = wrapper.find('ul.infos').at(1)
      const offerInfosSubElements = offerInfosElement.find('li')
      expect(offerInfosSubElements.at(0).prop('title')).toBe(
        'entre 2 et 5 personnes'
      )

      const userPictoComponent = offerInfosSubElements.at(0).find(Icon)
      expect(userPictoComponent).toBeDefined()
      expect(userPictoComponent.prop('svg')).toBe('picto-group')

      const numberOfParticipantsLabel = offerInfosSubElements.at(0).find('p')
      expect(numberOfParticipantsLabel.text()).toBe('2 - 5')
    })

    describe('when offer is an event product ', () => {
      it('should display the correct text when 0 ticket available', () => {
        // given
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = []
        props.stockAlertMessage = 'plus de places'
        props.offer = {
          id: '1M',
          activeMediation: {isActive: true, thumbUrl: 'https://url.to/thumb'},
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2019-02-25T09:50:10.735519Z',
          dateModifiedAtLastProvider: '2019-02-25T09:50:31.598542Z',
          productId: 42,
          idAtProviders: null,
          isActive: true,
          isEvent: true,
          isThing: false,
          lastProviderId: null,
          modelName: 'Offer',
          venueId: 'BE',
          mediationsIds: ['EY'],
          stocksIds: ['JQ'],
        }

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const ulElements = wrapper.find('ul')
        const stockAvailabilityElement = ulElements
          .at(1)
          .find('li')
          .at(3)
        expect(stockAvailabilityElement.text()).toBe('plus de places')
      })

      it('should display the correct text when 1 ticket is available', () => {
        // given
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = [{}]
        props.stockAlertMessage = 'encore 1 place'
        props.offer = {
          id: '1M',
          activeMediation: {isActive: true, thumbUrl: 'https://url.to/thumb'},
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2019-02-25T09:50:10.735519Z',
          dateModifiedAtLastProvider: '2019-02-25T09:50:31.598542Z',
          productId: 42,
          idAtProviders: null,
          isActive: true,
          isEvent: true,
          isThing: false,
          lastProviderId: null,
          modelName: 'Offer',
          venueId: 'BE',
          mediationsIds: ['EY'],
          stocksIds: ['JQ'],
        }

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const ulElements = wrapper.find('ul')
        const stockAvailabilityElement = ulElements
          .at(1)
          .find('li')
          .at(3)
        expect(stockAvailabilityElement.text()).toBe('encore 1 place')
      })

      it('should display the correct text when 2 tickets are available', () => {
        // given
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = [{}, {}]
        props.stockAlertMessage = 'encore 2 places'
        props.offer = {
          id: '1M',
          activeMediation: {isActive: true, thumbUrl: 'https://url.to/thumb'},
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2019-02-25T09:50:10.735519Z',
          dateModifiedAtLastProvider: '2019-02-25T09:50:31.598542Z',
          productId: 42,
          idAtProviders: null,
          isActive: true,
          isEvent: true,
          isThing: false,
          lastProviderId: null,
          modelName: 'Offer',
          venueId: 'BE',
          mediationsIds: ['EY'],
          stocksIds: ['JQ'],
        }

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const ulElements = wrapper.find('ul')
        const stockAvailabilityElement = ulElements
          .at(1)
          .find('li')
          .at(3)
        expect(stockAvailabilityElement.text()).toBe('encore 2 places')
      })

      it('should display the correct text "2 dates" on the link redirecting to the offer management', () => {
        // given
        const options = {
          context: {
            router: {
              history: {
                push: jest.fn(),
                replace: jest.fn(),
                createHref: jest.fn(),
              },
              route: {
                location: {},
                match: {},
              },
            },
          },
          childContextTypes: {
            router: jest.fn(),
          },
        }
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = [{}, {}]
        props.offer = {
          id: '1M',
          activeMediation: {isActive: true, thumbUrl: 'https://url.to/thumb'},
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2019-02-25T09:50:10.735519Z',
          dateModifiedAtLastProvider: '2019-02-25T09:50:31.598542Z',
          productId: 42,
          idAtProviders: null,
          isActive: true,
          isEvent: true,
          isThing: false,
          lastProviderId: null,
          modelName: 'Offer',
          venueId: 'BE',
          mediationsIds: ['EY'],
          stocksIds: ['JQ'],
        }

        // when
        const wrapper = mount(<OfferItem {...props} />, options)

        // then
        const ulElements = wrapper.find('ul')
        const navLinkComponent = ulElements
          .at(1)
          .find('li')
          .at(1)
          .find(NavLink)
        expect(navLinkComponent.prop('className')).toBe('has-text-primary')
        expect(navLinkComponent.prop('to')).toBe('/offres/1M?gestion')
        expect(navLinkComponent.text()).toBe('2 dates')
      })
    })

    describe('when offer is a thing product', () => {
      it('should display the correct text when 0 thing is available', () => {
        // given
        props.product = {
          offerType: { label: 'Une place de cinéma' },
        }
        props.stocks = []
        props.stockAlertMessage = 'plus de stock'
        props.offer = {
          activeMediation: {isActive: true, thumbUrl: 'https://url.to/thumb'},
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2019-02-25T09:50:10.735519Z',
          dateModifiedAtLastProvider: '2019-02-25T09:50:31.598542Z',
          id: '1M',
          idAtProviders: null,
          isActive: true,
          isEvent: false,
          isThing: true,
          lastProviderId: null,
          mediationsIds: ['EY'],
          modelName: 'Offer',
          productId: 42,
          stocksIds: ['JQ'],
          venueId: 'BE',
        }

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const ulElements = wrapper.find('ul')
        const stockAvailabilityElement = ulElements
          .at(1)
          .find('li')
          .at(3)
        expect(stockAvailabilityElement.text()).toBe('plus de stock')
      })

      it('should display the correct text "1 prix" on the link redirecting to the offer management', () => {
        // given
        const options = {
          context: {
            router: {
              history: {
                push: jest.fn(),
                replace: jest.fn(),
                createHref: jest.fn(),
              },
              route: {
                location: {},
                match: {},
              },
            },
          },
          childContextTypes: {
            router: jest.fn(),
          },
        }
        props.product = {
          offerType: { label: 'Une place de cinéma' },
        }
        props.stocks = [{}]
        props.offer = {
          id: '1M',
          activeMediation: {isActive: true, thumbUrl: 'https://url.to/thumb'},
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2019-02-25T09:50:10.735519Z',
          dateModifiedAtLastProvider: '2019-02-25T09:50:31.598542Z',
          productId: 42,
          idAtProviders: null,
          isActive: true,
          isEvent: false,
          isThing: true,
          lastProviderId: null,
          modelName: 'Offer',
          venueId: 'BE',
          mediationsIds: ['EY'],
          stocksIds: ['JQ'],
        }

        // when
        const wrapper = mount(<OfferItem {...props} />, options)

        // then
        const ulElements = wrapper.find('ul')
        const navLinkComponent = ulElements
          .at(1)
          .find('li')
          .at(1)
          .find(NavLink)
        expect(navLinkComponent.prop('className')).toBe('has-text-primary')
        expect(navLinkComponent.prop('to')).toBe('/offres/1M?gestion')
        expect(navLinkComponent.text()).toBe('1 prix')
      })
    })
  })
})
