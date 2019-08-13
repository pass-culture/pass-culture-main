import { shallow } from 'enzyme'
import React from 'react'

import { distanceOptions, INFINITE_DISTANCE } from '../helpers'
import FilterByDistance from '../FilterByDistance'

describe('src | components | pages | search | FilterControls | FilterByDistance', () => {
  let props

  beforeEach(() => {
    props = {
      filterActions: {
        add: jest.fn(),
        change: jest.fn(),
        remove: jest.fn(),
      },
      filterState: {
        isNew: false,
        params: {
          categories: null,
          date: null,
          distance: null,
          jours: null,
          latitude: null,
          longitude: null,
          'mots-cles': null,
          orderBy: 'offer.id+desc',
        },
      },
      geolocation: {
        latitude: null,
        longitude: null,
        watchId: null,
      },
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<FilterByDistance {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('handleOnChangeDistance()', () => {
    describe('i am not geolocated', () => {
      it('should set the distance to 1 when I change the select field to 1', () => {
        // given
        const distance = 1
        const event = {
          target: {
            value: distance,
          },
        }
        const wrapper = shallow(<FilterByDistance {...props} />)

        // when
        wrapper.instance().handleOnChangeDistance(event)

        // then
        expect(props.filterActions.change).toHaveBeenCalledWith({
          distance,
          latitude: null,
          longitude: null,
        })
      })
    })

    describe('i am geolocated', () => {
      it('should set the distance to 1 when I change the select field to 1', () => {
        // given
        props.geolocation.latitude = 48.854892
        props.geolocation.longitude = 2.532037
        const distance = 1
        const event = {
          target: {
            value: distance,
          },
        }
        const wrapper = shallow(<FilterByDistance {...props} />)

        // when
        wrapper.instance().handleOnChangeDistance(event)

        // then
        expect(props.filterActions.change).toHaveBeenCalledWith({
          distance,
          latitude: props.geolocation.latitude,
          longitude: props.geolocation.longitude,
        })
      })

      it('should set the distance to infinite when I change the select field to infinite and clear the geolocation', () => {
        // given
        props.geolocation.latitude = 48.854892
        props.geolocation.longitude = 2.532037
        const distance = INFINITE_DISTANCE
        const event = {
          target: {
            value: distance,
          },
        }
        const wrapper = shallow(<FilterByDistance {...props} />)

        // when
        wrapper.instance().handleOnChangeDistance(event)

        // then
        expect(props.filterActions.change).toHaveBeenCalledWith({
          distance,
          latitude: null,
          longitude: null,
        })
      })
    })
  })

  describe('render()', () => {
    it('should have four options with right values by default', () => {
      // given
      const wrapper = shallow(<FilterByDistance {...props} />)

      // when
      const optionsMarkup = wrapper.find('option')
      const { defaultValue } = wrapper.find('select').props()

      // then
      expect(optionsMarkup).toHaveLength(4)
      optionsMarkup.forEach((option, index) => {
        expect(option.props().value).toBe(distanceOptions[index].value)
      })
      expect(defaultValue).toBe(INFINITE_DISTANCE)
    })

    it('should have 50 km selected when I have 50 in distance parameter', () => {
      // given
      props.filterState.params.distance = '50'
      const wrapper = shallow(<FilterByDistance {...props} />)

      // when
      const { defaultValue } = wrapper.find('select').props()

      // then
      expect(defaultValue).toBe(props.filterState.params.distance)
    })

    it('should display geolocation warning if no geolocation', () => {
      // when
      const wrapper = shallow(<FilterByDistance {...props} />)

      // then
      const warningMessage = wrapper.find('.geoloc-warning').text()
      const selectInput = wrapper.find('select').props()

      expect(selectInput).toHaveProperty('disabled', true)
      expect(warningMessage).toBe('Activez votre géolocalisation pour utiliser ce filtre.')
    })

    it('should not display geolocation warning if geolocation is active', () => {
      // given
      props.geolocation = {
        latitude: 1.1,
        longitude: 2.2,
        watchId: 1,
      }

      // when
      const wrapper = shallow(<FilterByDistance {...props} />)

      // then
      const warningMessage = wrapper.find('.geoloc-warning')
      const selectInput = wrapper.find('select').props()

      expect(selectInput).toHaveProperty('disabled', false)
      expect(warningMessage).toHaveLength(0)
    })
  })
})
