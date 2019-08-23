import { shallow } from 'enzyme'
import React from 'react'

import BackLink from '../BackLink'
import CloseLink from '../CloseLink/CloseLink'
import Header from '../Header'
import SubmitButton from '../SubmitButton'

describe('src | components | layout | Header | Header', () => {
  let props

  beforeEach(() => {
    props = {
      history: {
        push: () => {},
        replace: () => {},
      },
      location: {
        pathname: '',
        search: '',
      },
      match: {
        params: {},
      },
      title: 'Fake header title',
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Header {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should display the header by default', () => {
      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      const backLink = wrapper.find(BackLink)
      const h1 = wrapper.find('h1').text()
      const closeLink = wrapper.find(CloseLink).props().closeTo
      const submitButton = wrapper.find(SubmitButton)
      expect(backLink).toHaveLength(0)
      expect(h1).toBe('Fake header title')
      expect(closeLink).toBe('/decouverte')
      expect(submitButton).toHaveLength(0)
    })

    it('should display the back link', () => {
      // given
      props.backTo = '/fakeurl'

      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      const backLink = wrapper.find(BackLink)
      expect(backLink).toHaveLength(1)
    })

    it('should display the close link', () => {
      // given
      props.closeTo = '/fakeurl'

      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      const closeLink = wrapper.find(CloseLink).props().closeTo
      expect(closeLink).toBe('/fakeurl')
    })

    it('should display the submit button', () => {
      // given
      props.useSubmit = true

      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      const submitButton = wrapper.find(SubmitButton)
      expect(submitButton).toHaveLength(1)
    })
  })
})
