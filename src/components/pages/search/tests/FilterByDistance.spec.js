import { shallow } from 'enzyme'
import React from 'react'

import options, {
  INFINITE_DISTANCE,
} from '../../../../helpers/search/distanceOptions'
import { FilterByDistance } from '../FilterByDistance'

describe('src | components | pages | search | FilterByDistance', () => {
  const fakeMethod = jest.fn()
  let props

  beforeEach(() => {
    props = {
      filterActions: {
        add: fakeMethod,
        change: fakeMethod,
        remove: fakeMethod,
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
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('onChangeDistance()', () => {
    describe('when I am not geolocated', () => {
      it('should change the distance to 1', () => {
        // given
        const distance = 1
        const event = {
          target: {
            value: distance,
          },
        }
        const expected = {
          distance,
          latitude: null,
          longitude: null,
        }

        // when
        const wrapper = shallow(<FilterByDistance {...props} />)
        wrapper.instance().onChangeDistance(event)

        // then
        expect(props.filterActions.change).toHaveBeenCalledWith(expected)
      })
    })

    describe('when I am geolocated', () => {
      it('should change the distance to 1', () => {
        // given
        props.geolocation.latitude = 48.854892
        props.geolocation.longitude = 2.532037
        const distance = 1
        const event = {
          target: {
            value: distance,
          },
        }
        const expected = {
          distance,
          latitude: props.geolocation.latitude,
          longitude: props.geolocation.longitude,
        }

        // when
        const wrapper = shallow(<FilterByDistance {...props} />)
        wrapper.instance().onChangeDistance(event)

        // then
        expect(props.filterActions.change).toHaveBeenCalledWith(expected)
        props.filterActions.change.mockClear()
      })

      it('should change the distance to infinite and clear the geolocation', () => {
        // given
        props.geolocation.latitude = 48.854892
        props.geolocation.longitude = 2.532037
        const distance = INFINITE_DISTANCE
        const event = {
          target: {
            value: distance,
          },
        }
        const expected = {
          distance,
          latitude: null,
          longitude: null,
        }

        // when
        const wrapper = shallow(<FilterByDistance {...props} />)
        wrapper.instance().onChangeDistance(event)

        // then
        expect(props.filterActions.change).toHaveBeenCalledWith(expected)
        props.filterActions.change.mockClear()
      })
    })
  })

  describe('render()', () => {
    it('should have four options with right values', () => {
      // when
      const wrapper = shallow(<FilterByDistance {...props} />)
      const optionsMarkup = wrapper.find('option')
      const { defaultValue } = wrapper.find('select').props()

      // then
      expect(optionsMarkup).toHaveLength(4)
      optionsMarkup.forEach((option, index) => {
        expect(option.props().value).toBe(options[index].value)
      })
      expect(defaultValue).toBe(20000)
    })

    it('should have 50 km selected', () => {
      // given
      props.filterState.params.distance = '50'

      // when
      const wrapper = shallow(<FilterByDistance {...props} />)
      const { defaultValue } = wrapper.find('select').props()

      // then
      expect(defaultValue).toBe(props.filterState.params.distance)
    })
  })
})
