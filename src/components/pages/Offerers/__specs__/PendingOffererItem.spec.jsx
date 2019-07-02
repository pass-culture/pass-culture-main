import React from 'react'
import { shallow } from 'enzyme'

import PendingOffererItem from '../PendingOffererItem'

describe('src | components | pages | Offerers | PendingOffererItem', () => {
  let change
  let dispatch
  let parse
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    change = jest.fn()
    parse = () => ({ 'mots-cles': null })

    props = {
      currentUser: {},
      dispatch,
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
        change,
        parse,
      },
      location: {
        search: '',
      },
    }
  })
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<PendingOffererItem {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
