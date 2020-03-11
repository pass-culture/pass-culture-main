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

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<OfferItem {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    describe('thumb Component', () => {
      it('should render a Thumb Component with the given url when offer has an active mediation', () => {
        // given
        const wrapper = shallow(<OfferItem {...props} />)

        // when
        const thumbComponent = wrapper.find(Thumb)

        // then
        expect(thumbComponent.prop('alt')).toBe('offre')
        expect(thumbComponent.prop('src')).toBe('https://url.to/thumb')
      })

      it('should render a Thumb Component with url from product when offer does not have an active mediation', () => {
        // given
        props.offer = activeOfferWithOutActiveMediation
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
        props.offer = activeOfferWithOutActiveMediation
        props.product.thumbUrl = null
        props.mediations = []
        const wrapper = shallow(<OfferItem {...props} />)

        // when
        const thumbComponent = wrapper.find(Thumb)

        // then
        expect(thumbComponent.prop('alt')).toBe('offre')
        expect(thumbComponent.prop('src')).toBe('')
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

      describe('preview link', () => {
        it('should not be displayed when offer has no active mediation', () => {
          // given
          props.offer = activeOfferWithOutActiveMediation

          const wrapper = shallow(<OfferItem {...props} />)

          // when
          const offerPreviewLink = wrapper.find('OfferPreviewLink')

          // then
          expect(offerPreviewLink).toHaveLength(0)
        })

        it('should be displayed when offer is no editable has an active mediation', () => {
          // given
          props.offer = activeOfferWithActiveMediationAndNotEditable
          const wrapper = shallow(<OfferItem {...props} />)

          // when
          const offerPreviewLink = wrapper.find('OfferPreviewLink')

          // then
          expect(offerPreviewLink).toHaveLength(1)
        })

        it('should be displayed when offer has an active mediation', () => {
          // given
          props.offer = activeOfferWithActiveMediation

          const wrapper = shallow(<OfferItem {...props} />)

          // when
          const offerPreviewLink = wrapper.find('OfferPreviewLink')

          // then
          expect(offerPreviewLink).toHaveLength(1)
          expect(offerPreviewLink.prop('href')).toMatch('/offre/details/M4/HA')
        })

        it('should open a new window with correct link', () => {
          // given
          props.offer = activeOfferWithActiveMediation

          const wrapper = shallow(<OfferItem {...props} />)
          const offerPreviewLink = wrapper.find('OfferPreviewLink')

          jest.spyOn(global.window, 'open').mockImplementation(() => Object.create(window))

          jest.spyOn(global.window, 'focus').mockImplementation(() => {})

          const url = 'http://localhost/offre/details/M4/HA'

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

      describe('edit offer link', () => {
        it('should be displayed when offer is editable', () => {
          // given
          props.offer = activeOfferWithActiveMediation

          const wrapper = shallow(<OfferItem {...props} />)

          // when
          const editOfferLink = wrapper.find('.edit-link')

          // then
          expect(editOfferLink).toHaveLength(1)
        })

        it('should not be displayed when offer is no editable', () => {
          // given
          props.offer = activeOfferWithActiveMediationAndNotEditable
          const wrapper = shallow(<OfferItem {...props} />)

          // when
          const editOfferLink = wrapper.find('.edit-link')

          // then
          expect(editOfferLink).toHaveLength(0)
        })
      })

      describe('mediations link', () => {
        it('should display a link to offer when offer has one or more mediations', () => {
          // given
          props.offer = activeOfferWithActiveMediation
          const wrapper = shallow(<OfferItem {...props} />)

          // when
          const addMediationsLink = wrapper.find('.add-mediations-link')
          const textSpan = addMediationsLink.find('span').at(1)
          const icon = addMediationsLink.find('Icon')

          // then
          expect(addMediationsLink).toHaveLength(1)
          expect(addMediationsLink.prop('className')).toBe(
            'button is-small is-secondary add-mediations-link'
          )
          expect(addMediationsLink.prop('to')).toBe('/offres/M4')
          expect(icon.prop('svg')).toBe('ico-stars')
          expect(textSpan.text()).toBe('Accroches')
        })

        it('should display a link to add a mediation when offer no mediations yet', () => {
          // given
          props.mediations = []
          props.offer = activeOfferWithOutActiveMediation

          const wrapper = shallow(<OfferItem {...props} />)

          // when
          const addMediationsLink = wrapper.find('.add-mediations-link')
          const textSpan = addMediationsLink.find('span').at(1)
          const icon = addMediationsLink.find('Icon')

          // thenu
          expect(addMediationsLink).toHaveLength(1)
          expect(addMediationsLink.prop('className')).toBe(
            'button is-small is-primary is-outlined add-mediations-link'
          )
          expect(addMediationsLink.prop('to')).toBe(
            '/offres/GH/accroches/nouveau?orderBy=offer.id+desc'
          )
          expect(icon.prop('svg')).toBe('ico-stars')
          expect(textSpan.text()).toBe('Ajouter une Accroche')
        })
      })
    })

    describe('offer title', () => {
      it('should display title from offer and not use product details', () => {
        // Given
        props.offer.name = 'Harry Potter vol.1'
        props.product.name = 'Harry Potter vol.2'

        // When
        const wrapper = shallow(<OfferItem {...props} />)

        // Then
        const firstLink = wrapper.find(NavLink).first()
        expect(firstLink.prop('title')).toStrictEqual('Harry Potter vol.1')
      })

      it('should contain a Navlink Component with the right props and containing a DotDotDot component', () => {
        // given
        props.offer.name = 'fake name'
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
        props.availabilityMessage = 'Plus de stock restant'
        props.offer = activeOfferWithActiveMediation

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const ulElements = wrapper.find('ul')
        const stockAvailabilityElement = ulElements
          .at(1)
          .find('li')
          .at(3)
        expect(stockAvailabilityElement.text()).toBe('Plus de stock restant')
      })

      it('should display the correct text when 1 ticket is available', () => {
        // given
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = [{}]
        props.availabilityMessage = 'Encore 1 stock restant'
        props.offer = activeOfferWithActiveMediation

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const ulElements = wrapper.find('ul')
        const stockAvailabilityElement = ulElements
          .at(1)
          .find('li')
          .at(3)
        expect(stockAvailabilityElement.text()).toBe('Encore 1 stock restant')
      })

      it('should display the correct text when 2 tickets are available', () => {
        // given
        props.product = {
          offerType: { label: 'Conférence — Débat — Dédicace' },
        }
        props.stocks = [{}, {}]
        props.availabilityMessage = 'Encore 2 stocks restant'
        props.offer = activeOfferWithActiveMediation

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const ulElements = wrapper.find('ul')
        const stockAvailabilityElement = ulElements
          .at(1)
          .find('li')
          .at(3)
        expect(stockAvailabilityElement.text()).toBe('Encore 2 stocks restant')
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
        props.offer = activeOfferWithActiveMediation

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
        expect(navLinkComponent.prop('to')).toBe('/offres/M4?gestion')
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
        props.availabilityMessage = 'Plus de stock restant'
        props.offer = activeThingOfferWithActiveMediation

        // when
        const wrapper = shallow(<OfferItem {...props} />)

        // then
        const ulElements = wrapper.find('ul')
        const stockAvailabilityElement = ulElements
          .at(1)
          .find('li')
          .at(3)
        expect(stockAvailabilityElement.text()).toBe('Plus de stock restant')
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
        props.offer = activeThingOfferWithActiveMediation

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
        expect(navLinkComponent.prop('to')).toBe('/offres/THING?gestion')
        expect(navLinkComponent.text()).toBe('1 prix')
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
