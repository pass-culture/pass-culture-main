import React from 'react'
import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'

import Typeform from '../Typeform'

const history = createBrowserHistory()
history.push('/typeform')

describe('src | components | pages | typeform | Typeform', () => {
  describe('when user has filled the cultural survey', () => {
    it('should redirect to /bienvenue when request to API is successful', () => {
      // given
      const props = {
        history: {
          push: jest.fn(),
        },
        flagUserHasFilledTypeform: (id, handleSuccess) => {
          handleSuccess()
        },
      }

      const wrapper = mount(<Typeform {...props} />)

      // when
      wrapper.instance().onSubmitTypeForm()

      // then
      expect(props.history.push).toHaveBeenCalledWith('/bienvenue')
    })
  })

  describe('when user has not filled the cultural survey', () => {
    it('should display typeform when user has not filled the cultural survey', () => {
      // given
      const props = {
        history: {
          push: jest.fn(),
        },
        flagUserHasFilledTypeform: jest.fn(),
      }

      // when
      const wrapper = mount(<Typeform {...props} />)

      const typeform = wrapper.find('.react-embed-typeform-container')

      // then
      expect(typeform).toHaveLength(1)
    })
  })
})
