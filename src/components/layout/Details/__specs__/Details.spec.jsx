import React from 'react'
import { shallow } from 'enzyme'

import Details from '../Details'

describe('src | components | layout | Details', () => {
  let props

  beforeEach(() => {
    props = {
      hasReceivedData: false,
      history: {
        push: jest.fn(),
        replace: jest.fn()
      },
      location: {
        pathname: '',
        search: ''
      },
      match: {
        params: {
          details: undefined
        }
      },
      needsToRequestGetData: jest.fn(),
      requestGetData: jest.fn()
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Details {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
