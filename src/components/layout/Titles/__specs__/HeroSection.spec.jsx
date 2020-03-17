import React from 'react'
import { shallow } from 'enzyme'

import Titles from '../Titles'

describe('src | components | layout | Titles', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      subtitle: 'Fake subtitle',
      title: 'Fake title',
    }

    // when
    const wrapper = shallow(<Titles {...props}> </Titles>)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    describe('subtitle', () => {
      it('should display subtitle when given', () => {
        // given
        const props = {
          subtitle: 'Fake subtitle',
          title: 'Fake title',
        }

        // when
        const wrapper = shallow(<Titles {...props} />)
        const subtitle = wrapper.find('h2')

        // then
        expect(subtitle).toHaveLength(1)
        expect(subtitle.text()).toBe('FAKE SUBTITLE')
      })
    })
  })
})
