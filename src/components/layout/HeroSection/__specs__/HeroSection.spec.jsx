import React from 'react'
import { shallow } from 'enzyme'

import HeroSection from '../HeroSection'

describe('src | components | layout | HeroSection', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      subtitle: 'Fake subtitle',
      title: 'Fake title',
    }

    // when
    const wrapper = shallow(<HeroSection {...props}> </HeroSection>)

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
        const wrapper = shallow(<HeroSection {...props} />)
        const subtitle = wrapper.find('h2')

        // then
        expect(subtitle).toHaveLength(1)
        expect(subtitle.text()).toBe('FAKE SUBTITLE')
      })
    })
  })
})
