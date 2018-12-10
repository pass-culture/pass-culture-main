// jest --env=jsdom ./src/components/pages/forgot-password/tests/ResetThePasswordForm --watch
import React from 'react'
import { shallow } from 'enzyme'
import { RawResetThePasswordForm } from '../ResetThePasswordForm'

describe('src |  components |  pages |  forgot-password |  ResetThePasswordForm', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = { canSubmit: true, isLoading: false }
      // when
      const wrapper = shallow(<RawResetThePasswordForm {...props} />)
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
