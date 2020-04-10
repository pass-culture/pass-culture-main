import React from 'react'
import { shallow, mount } from 'enzyme'
import { Redirect } from 'react-router-dom'
import { createBrowserHistory } from 'history'

import Typeform from '../Typeform'

const history = createBrowserHistory()
history.push('/typeform')

describe('src | components | pages | typeform | Typeform', () => {
  describe('when user has filled the cultural survey', () => {
    it('should redirect to /bienvenue when user has filled the cultural survey', () => {
      // given
      const props = {
        flagUserHasFilledTypeform: jest.fn(),
        needsToFillCulturalSurvey: false,
      }

      // when
      const wrapper = shallow(<Typeform {...props} />)

      const redirect = wrapper.find(Redirect)

      // then
      expect(redirect).toHaveLength(1)
      expect(redirect.prop('to')).toBe('/bienvenue')
    })
  })

  describe('when user has not filled the cultural survey', () => {
    it('should display typeform when user has not filled the cultural survey', () => {
      // given
      const props = {
        flagUserHasFilledTypeform: jest.fn(),
        needsToFillCulturalSurvey: true,
      }

      // when
      const wrapper = mount(<Typeform {...props} />)

      const typeform = wrapper.find('.react-embed-typeform-container')

      // then
      expect(typeform).toHaveLength(1)
    })
  })
})
