import React from 'react'
import VenueProviderItem from '../VenueProviderItem'
import { shallow } from 'enzyme'
import { Icon } from 'pass-culture-shared'
import { NavLink } from 'react-router-dom'

describe('src | components | pages | Venue | VenueProvidersManager | VenueProviderItem', () => {
  let props
  let dispatch

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      dispatch,
      venueProvider: {
        id: 1,
        isActive: true,
        lastSyncDate: '2018-01-01',
        nOffers: 1,
        provider: {
          name: 'fake local class',
          localClass: 'OpenAgendaEvents'
        },
        venueId: 1,
        venueIdAtOfferProvider: 1
      }
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<VenueProviderItem {...props}/>)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should contain an Icon component with the right props', () => {
      // when
      const wrapper = shallow(<VenueProviderItem {...props}/>)

      // then
      const icon = wrapper.find('.picto').find(Icon)
      expect(icon).toHaveLength(1)
      expect(icon.prop('svg')).toBe('logo-openAgenda')
    })

    it('should render provider local class when provided', () => {
      // when
      const wrapper = shallow(<VenueProviderItem {...props} />)

      // then
      const providerLocalClass = wrapper.find('.provider-name-container')
      expect(providerLocalClass.text()).toBe('fake local class')
    })

    it('should render venue id at offer provider when provided', () => {
      // when
      const wrapper = shallow(<VenueProviderItem {...props} />)

      // then
      const venueIdAtOfferProvider = wrapper.find('strong.has-text-weight-bold')
      expect(venueIdAtOfferProvider.text()).toBe('1')
    })

    it('should render the number of offers when data of provider were already synced and offers are provided', () => {
      // when
      const wrapper = shallow(<VenueProviderItem {...props} />)

      // then
      const navLink = wrapper.find(NavLink)
      expect(navLink).toBeDefined()
      expect(navLink.prop('to')).toBe('/offres?lieu=1')
      expect(navLink.prop('className')).toBe('has-text-primary')
      const icon = navLink.find(Icon)
      expect(icon).toBeDefined()
      expect(icon.prop('svg')).toBe('ico-offres-r')
      const numberOfOffersLabel = navLink.find('.number-of-offers-label')
      expect(numberOfOffersLabel).toHaveLength(1)
      expect(numberOfOffersLabel.text()).toBe('1 offre')
    })

    it('should render zero offers label when data of provider were already synced and no offers', () => {
      // given
      props.venueProvider.nOffers = 0

      // when
      const wrapper = shallow(<VenueProviderItem {...props} />)

      // then
      const numberOfOffersLabel = wrapper.find('.offers-container')
      expect(numberOfOffersLabel).toHaveLength(1)
      expect(numberOfOffersLabel.text()).toBe('0 offre')
    })
  })
})
