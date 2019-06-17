import React from 'react'
import { shallow } from 'enzyme'

import OffererItem from '../OffererItem'

const dispatchMock = jest.fn()
const parseMock = () => ({ 'mots-cles': null })
const queryChangeMock = jest.fn()

describe('src | components | pages | Offerers | OffererItem', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        currentUser: {},
        dispatch: dispatchMock,
        offerers: [{
          id: 'AE',
          name: 'Fake Name',
          nOffers: 56,
          isValidated: true
       }],
        pagination: {
          apiQuery: {
            keywords: null,
          },
        },
        query: {
          change: queryChangeMock,
          parse: parseMock,
        },
        location: {
          search: '',
        },
        venues: [
          {}
        ],
        physicalVenues: [{}]
      }

      // when
      const wrapper = shallow(<OffererItem {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
