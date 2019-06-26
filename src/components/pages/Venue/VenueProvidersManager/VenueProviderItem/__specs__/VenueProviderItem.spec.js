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
          localClass: 'fake local class'
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
      expect(icon.prop('svg')).toBe('picto-db-default')
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
    })

    it('should render the label "en cours de validation" when provider is not synced yet', () => {
      // given
      props.venueProvider.lastSyncDate = null

      // when
      const wrapper = shallow(<VenueProviderItem {...props} />)

      // then
      const div = wrapper.find('.validation-label-container')
      expect(div.text()).toBe('En cours de validation')
    })
  })
})
