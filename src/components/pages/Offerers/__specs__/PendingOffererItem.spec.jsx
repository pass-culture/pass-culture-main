import React from 'react'
import { shallow } from 'enzyme'

import PendingOffererItem from '../PendingOffererItem'

const dispatchMock = jest.fn()
const parseMock = () => ({ 'mots-cles': null })
const queryChangeMock = jest.fn()

describe('src | components | pages | Offerers | PendingOffererItem', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        currentUser: {},
        dispatch: dispatchMock,
        offerer: {
          name: 'Fake Name',
          siren: '123456789'
        },
        pendingPendingOffererItem: [],
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
      }

      // when
      const wrapper = shallow(<PendingOffererItem {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
