import React from 'react'
import { shallow } from 'enzyme'

import Details from '../Details'
import RectoContainer from '../../Recto/RectoContainer'
import VersoContainer from '../../Verso/VersoContainer'

describe('src | components | layout | Details | Details', () => {
  let props

  beforeEach(() => {
    props = {
      hasReceivedData: false,
      history: {
        push: jest.fn(),
        replace: jest.fn(),
      },
      location: {
        pathname: '',
        search: '',
      },
      match: {
        params: {
          details: undefined,
        },
      },
      needsToRequestGetData: false,
      requestGetData: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Details {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should render just VersoContainer', () => {
      // when
      const wrapper = shallow(<Details {...props} />)

      // then
      const versoContainer = wrapper.find(VersoContainer)
      expect(versoContainer).toHaveLength(1)
    })

    it('should render VersoContainer and RectoContainer', () => {
      // given

      // when
      const wrapper = shallow(<Details {...props} />)
      wrapper.setState({ forceDetailsVisible: true })

      // then
      const versoContainer = wrapper.find(VersoContainer)
      const rectoContainer = wrapper.find(RectoContainer)
      expect(versoContainer).toHaveLength(1)
      expect(rectoContainer).toHaveLength(1)
    })
  })
})
