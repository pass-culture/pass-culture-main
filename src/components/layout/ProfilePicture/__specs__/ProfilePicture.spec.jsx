import React from 'react'
import { shallow } from 'enzyme'

import ProfilePicture from '../ProfilePicture'

import { ROOT_PATH } from '../../../../utils/config'

describe('src | components | pages | ProfilePicture', () => {
  it('should match the snapshot', () => {
    // given
    const props = {}

    // when
    const wrapper = shallow(<ProfilePicture {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should display image with the right url', () => {
      // given
      const props = {
        colored: false,
      }

      // when
      const wrapper = shallow(<ProfilePicture {...props} />)
      const img = wrapper.find('img').props()

      // then
      expect(img.src).toBe(`${ROOT_PATH}/icons/ico-user-circled-white.svg`)
      expect(img.alt).toBe('Avatar')
    })
  })
})
