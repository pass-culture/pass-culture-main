import React from 'react'
import {shallow} from 'enzyme'
import CreationControl from "../CreationControl"

describe('src | components | pages | Offerer | CreationControl ', () => {
  let props

  beforeEach(() => {
    props = {
      parseFormChild: (a) => { return a }
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<CreationControl {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
