import { shallow } from 'enzyme'
import LocationViewer from '../LocationViewer'
import React from 'react'

describe('src | components | pages | Venue | fields | LocationViewer', () => {
  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<LocationViewer />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
