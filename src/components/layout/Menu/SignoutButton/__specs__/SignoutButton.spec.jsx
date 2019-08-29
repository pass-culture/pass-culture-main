import { shallow } from 'enzyme'
import React from 'react'

import SignoutButton from '../SignoutButton'
import Icon from '../../../Icon'

describe('src | components | menu | SignoutButton', () => {
  let props

  beforeEach(() => {
    props = {
      onSignoutClick: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<SignoutButton {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should render one button and one Icon', () => {
      // given
      const wrapper = shallow(<SignoutButton {...props} />)

      // when
      const button = wrapper.find('button')
      const icon = wrapper.find(Icon)
      const text = wrapper.find('.pt5').text()

      // then
      expect(button).toHaveLength(1)
      expect(icon).toHaveLength(1)
      expect(text).toBe('Déconnexion')
    })
  })
})
