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
      events: [{}],
      things: [{}],
      venue: {
        id: 1
      },
      venueProvider: {
        id: 1,
        isActive: true,
        lastSyncDate: '2018-01-01',
        provider: {
          localClass: 'fake local class'
        },
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
      const providerLocalClass = wrapper.find('.has-text-weight-bold.is-size-3')
      expect(providerLocalClass.text()).toBe('fake local class')
    })

    it('should render venue id at offer provider when provided', () => {
      // when
      const wrapper = shallow(<VenueProviderItem {...props} />)

      // then
      const venueIdAtOfferProvider = wrapper.find('strong.has-text-weight-bold')
      expect(venueIdAtOfferProvider.text()).toBe('[1]')
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

    it('should render the enable button when data of provider were already synced and offers are provided and is active', () => {
      // given
      props.venueProvider.isActive = true

      // when
      const wrapper = shallow(<VenueProviderItem {...props} />)

      // then
      const button = wrapper.find('button').at(0)
      expect(button.prop('className')).toBe('button is-secondary')
      expect(button.prop('onClick')).toEqual(expect.any(Function))
      expect(button.text()).toBe('Désactiver')
    })

    it('should render the disable button when data of provider were already synced and offers are provided and is not active', () => {
      // given
      props.venueProvider.isActive = false

      // when
      const wrapper = shallow(<VenueProviderItem {...props} />)

      // then
      const button = wrapper.find('button').at(0)
      expect(button.prop('className')).toBe('button is-secondary')
      expect(button.prop('onClick')).toEqual(expect.any(Function))
      expect(button.text()).toBe('Activer')
    })

    it('should render the label "en cours de validation" when provider is not synced yet', () => {
      // given
      props.venueProvider.lastSyncDate = null

      // when
      const wrapper = shallow(<VenueProviderItem {...props} />)

      // then
      const div = wrapper.find('.small')
      expect(div.text()).toBe('En cours de validation')
    })
  })

  describe('click on buttons', () => {
    describe('deactivate', () => {
      it('should update venue provider active status using API', () => {
        // given
        const wrapper = shallow(<VenueProviderItem {...props} />)
        const deactivateButton = wrapper.find('button').at(0)

        // when
        deactivateButton.simulate('click')

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/venueProviders/1',
            body: {isActive: true},
            method: 'PATCH'
          },
          type: 'REQUEST_DATA_PATCH_/VENUEPROVIDERS/1'
        })
      })
    })

    describe('delete', () => {
      it('should delete venue provider using API', () => {
        // given
        const wrapper = shallow(<VenueProviderItem {...props} />)
        const deleteButton = wrapper.find('button').at(1)

        // when
        deleteButton.simulate('click')

        // then
        expect(dispatch).toHaveBeenCalledWith( {
          config: {
            apiPath: '/venueProviders/1',
            method: 'DELETE',
            stateKey: 'venueProviders'
          },
          type: 'REQUEST_DATA_DELETE_VENUEPROVIDERS'
        })
      })
    })
  })
})
