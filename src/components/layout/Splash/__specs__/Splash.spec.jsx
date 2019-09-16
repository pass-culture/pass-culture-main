import Splash from '../Splash'
import React from 'react'
import { shallow } from 'enzyme'

describe('src | components | layout | Splash', () => {
  let props

  beforeEach(() => {
    props = {
      closeTimeout: 1000,
      dispatch: jest.fn(),
      isBetaPage: true,
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Splash {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
