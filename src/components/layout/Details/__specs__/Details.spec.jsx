import React from 'react'
import { shallow } from 'enzyme'

import Details from '../Details'
import VersoContainer from '../../Verso/VersoContainer'

describe('src | components | layout | Details | Details', () => {
  let props

  beforeEach(() => {
    props = {
      bookingPath: 'fake/path',
      match: {
        params: {
          details: undefined,
        },
      },
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Details {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should render VersoContainer', () => {
      // when
      const wrapper = shallow(<Details {...props} />)

      // then
      const versoContainer = wrapper.find(VersoContainer)
      expect(versoContainer).toHaveLength(1)
    })
  })
})
