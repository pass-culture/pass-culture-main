import React from 'react'
import { shallow } from 'enzyme'

import PendingOffererItem from '../PendingOffererItem'

describe('src | components | pages | Offerers | OffererItem | PendingOffererItem', () => {
  let props

  beforeEach(() => {
    props = {
      offerer: {},
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<PendingOffererItem {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
