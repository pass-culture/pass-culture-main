import React from 'react'
import { mount, shallow } from 'enzyme'
import { Icon } from 'pass-culture-shared'

import { NavLink } from 'react-router-dom'
import Dotdotdot from 'react-dotdotdot'
import Thumb from '../../../../../components/layout/Thumb'

import OfferItem from '../OfferItem'
import offersMock from '../../__specs__/offersMock'

describe('src | components | pages | Offers | OfferItem', () => {
  let props

  beforeEach(() => {
    props = {
      aggregatedStock: {},
      dispatch: jest.fn(),
      offer: offersMock[0],
      mediations: [{ id: 'HA', isActive: true, thumbUrl: 'https://url.to/thumb' }],
      location: {
        search: '?orderBy=offer.id+desc',
      },
      maxDate: {
        format: jest.fn(),
      },
      offerTypeLabel: 'fake label',
      offerer: {},
      product: {},
      stockAlertMessage: 'fake alert message',
      stocks: [],
      venue: {
        name: 'Paris',
      },
      trackActivateOffer: jest.fn(),
      trackDeactivateOffer: jest.fn(),
      updateOffer: jest.fn(),
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
    it('should activate or deactivate offer', () => {
      // given
      const wrapper = shallow(<OfferItem {...props} />)
      const disableButton = wrapper.find('button')

      // when
      disableButton.simulate('click')

      // then
      expect(props.updateOffer).toHaveBeenCalledWith('M4', false)
    })
  })

  describe('render offer item', () => {
    describe('thumb Component', () => {
      it('should render a Thumb Component with the given url when offer has an active mediation', () => {
        // given
        props.offer.activeMediation = {
          id: 'EY',
          isActive: true,
          thumbUrl: 'https://url.to/thumb',
        }

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const thumbComponent = wrapper.find(Thumb)
        expect(thumbComponent.prop('alt')).toBe('offre')
        expect(thumbComponent.prop('src')).toBe('https://url.to/thumb')
      })

      it('should render a Thumb Component with url from product when offer does not have an active mediation', () => {
        // given
        props.offer.activeMediation = null
        props.product.thumbUrl = '/fake-product-url'
        props.mediations = []

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const thumbComponent = wrapper.find(Thumb)
        expect(thumbComponent.prop('alt')).toBe('offre')
        expect(thumbComponent.prop('src')).toBe('/fake-product-url')
      })

      it('should render a Thumb Component with an empty url when offer does not have an active mediation and product does not have a thumb url', () => {
        // given
        props.offer.activeMediation = null
        props.product.thumbUrl = null
        props.mediations = []

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const thumbComponent = wrapper.find(Thumb)
        expect(thumbComponent.prop('alt')).toBe('offre')
        expect(thumbComponent.prop('src')).toBe('')
      })
    })
    describe('action buttons', () => {
      describe('switch activate', () => {
        // TODO
        // Button exists
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
          expect(dispatch.mock.calls[0][0]).toStrictEqual(expectedParams)
        })
      })

      describe('preview link', () => {
        it('should not be displayed when offer has no active mediation', () => {
          // given
          props.offer = offersMock[1]

          const wrapper = shallow(<OfferItem {...props} />)

          // when
          const offerPreviewLink = wrapper.find('OfferPreviewLink')

          // then
          expect(offerPreviewLink).toHaveLength(0)
        })

        it('should be displayed when offer has an active mediation', () => {
          // given
          props.offer = {
            id: 'M4',
            activeMediation: {
              id: 'HA',
              isActive: true,
              thumbUrl: 'https://url.to/thumb',
            },
            bookingEmail: 'booking.email@test.com',
            dateCreated: '2019-02-25T09:50:10.735519Z',
            dateModifiedAtLastProvider: '2019-02-25T09:50:31.881297Z',
            idAtProviders: null,
            isActive: true,
            isEvent: false,
            isThing: true,
            lastProviderId: null,
            modelName: 'Offer',
            productId: 'EY',
            venueId: 'CU',
            mediationsIds: ['HA'],
            stocksIds: ['MQ'],
          }

          const wrapper = shallow(<OfferItem {...props} />)

          // when
          const offerPreviewLink = wrapper.find('OfferPreviewLink')

          // then
          expect(offerPreviewLink).toHaveLength(1)
          expect(offerPreviewLink.prop('href')).toMatch('/decouverte/M4/HA')
        })

        it('should open a new window with correct link', () => {
          // given
          props.offer = {
            id: 'M4',
            activeMediation: {
              id: 'HA',
              isActive: true,
              thumbUrl: 'https://url.to/thumb',
            },
            bookingEmail: 'booking.email@test.com',
            dateCreated: '2019-02-25T09:50:10.735519Z',
            dateModifiedAtLastProvider: '2019-02-25T09:50:31.881297Z',
            idAtProviders: null,
            isActive: true,
            isEvent: false,
            isThing: true,
            lastProviderId: null,
            modelName: 'Offer',
            productId: 'EY',
            venueId: 'CU',
            mediationsIds: ['HA'],
            stocksIds: ['MQ'],
          }

          const wrapper = shallow(<OfferItem {...props} />)
          const offerPreviewLink = wrapper.find('OfferPreviewLink')

          jest.spyOn(global.window, 'open').mockImplementation(() => Object.create(window))

          jest.spyOn(global.window, 'focus').mockImplementation(() => {})

          const url = 'http://localhost/decouverte/M4/HA'

          // when
          offerPreviewLink.simulate('click', { preventDefault: jest.fn() })

          // then
          expect(global.window.open).toHaveBeenCalledWith(
            url,
            'targetWindow',
            'toolbar=no,width=375,height=667'
          )
        })
      })

      describe('add mediations', () => {
        // TODO
      })

      describe('edit link', () => {
        // TODO
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
      expect(navLinkComponent.prop('className')).toBe('name')
      expect(navLinkComponent.prop('to')).toBe('/offres/M4?orderBy=offer.id+desc')
      expect(navLinkComponent.prop('title')).toBe('fake name')
      const dotdotdotComponent = navLinkComponent.find(Dotdotdot)
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
      expect(infosSubItems.at(1).text()).toStrictEqual('Structure : UGC')
      expect(infosSubItems.at(2).text()).toStrictEqual('Lieu : Paris')
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
      expect(offerInfosSubElements.at(0).prop('title')).toBe('entre 1 et 5 personnes')

      const userPictoComponent = offerInfosSubElements.at(0).find(Icon)
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
      expect(offerInfosSubElements.at(0).prop('title')).toBe('entre 2 et 5 personnes')

      const userPictoComponent = offerInfosSubElements.at(0).find(Icon)
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
          activeMediation: {
            id: 'EY',
            isActive: true,
            thumbUrl: 'https://url.to/thumb',
          },
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
          activeMediation: {
            id: 'EY',
            isActive: true,
            thumbUrl: 'https://url.to/thumb',
          },
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
          activeMediation: {
            id: 'EY',
            isActive: true,
            thumbUrl: 'https://url.to/thumb',
          },
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
          activeMediation: {
            id: 'EY',
            isActive: true,
            thumbUrl: 'https://url.to/thumb',
          },
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
          activeMediation: {
            id: 'EY',
            isActive: true,
            thumbUrl: 'https://url.to/thumb',
          },
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
          activeMediation: {
            id: 'EY',
            isActive: true,
            thumbUrl: 'https://url.to/thumb',
          },
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

  describe('event tracking', () => {
    it('should track deactivate offer when offer is active', () => {
      // given
      props.offer = {
        id: 'Xvgty46d',
        isActive: true,
      }

      const wrapper = shallow(<OfferItem {...props} />)

      // when
      wrapper.instance().handleOnDeactivateClick()

      // then
      expect(props.trackDeactivateOffer).toHaveBeenCalledWith('Xvgty46d')
    })

    it('should track activate offer when offer is inactive', () => {
      // given
      props.offer = {
        id: 'FG674FR',
        isActive: false,
      }
      const wrapper = shallow(<OfferItem {...props} />)

      // when
      wrapper.instance().handleOnDeactivateClick()

      // then
      expect(props.trackActivateOffer).toHaveBeenCalledWith('FG674FR')
    })
  })
})
