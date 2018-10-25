import React from 'react'
import { shallow } from 'enzyme'

import FormFooter from '../FormFooter'

describe('src | components | pages | signin | FormFooter', () => {
  describe.skip('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        cancel: null,
        className: 'fake className',
        submit: {
          url: 'fake url',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    describe('when cancel is defined and cancel url is present ', () => {
      it('should contain renderLinkButton', () => {
        // given
        const props = {
          cancel: {
            className: 'fake cancel className',
            disabled: false,
            label: 'fake cancel label',
            url: 'fake cancel url',
          },
          className: 'fake className',
        }

        // when
        const wrapper = shallow(<FormFooter {...props} />)
        const renderLinkButton = wrapper.find('Link').props()

        // then
        expect(renderLinkButton.id).toEqual('signin-signup-button')
      })
    })
    describe('when submit is defined and submit url is not present', () => {
      it('should contain renderSubmitButton', () => {
        // given
        const props = {
          className: 'fake className',
          submit: {
            className: 'fake submit className',
            disabled: false,
            label: 'fake submit label',
            url: '',
          },
        }

        // when
        const wrapper = shallow(<FormFooter {...props} />)
        const renderSubmitButton = wrapper.find('button').props()

        // then
        expect(renderSubmitButton.id).toEqual('signin-submit-button')
      })
    })
  })
})
