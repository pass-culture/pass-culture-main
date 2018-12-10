// jest --env=jsdom ./src/components/pages/forgot-password/tests/RequestEmailForm --watch
import React from 'react'
import { shallow } from 'enzyme'
import { RawRequestEmailForm } from '../RequestEmailForm'

describe('src | components | pages | forgot-password | RawRequestEmailForm', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = { canSubmit: true, isLoading: false }
      // when
      const wrapper = shallow(<RawRequestEmailForm {...props} />)
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
