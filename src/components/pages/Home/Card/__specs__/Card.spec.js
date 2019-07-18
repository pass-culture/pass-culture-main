import { shallow } from 'enzyme'
import Card from '../Card'
import React from 'react'

describe('src | components | pages | Home | Card', () => {
  let props

  beforeEach(() => {
    props = {
      navLink: 'http://nav.to/page',
      svg: 'my.svg',
      text: 'Coucou',
      title: 'Bienvenue',
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Card {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
