import React from 'react'
import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'

import Typeform from '../Typeform'

const history = createBrowserHistory()
history.push('/typeform')

jest.mock('uuid/v1', () => {
  return () => 1
})

describe('src | components | pages | typeform | Typeform', () => {
  describe('when user has filled the cultural survey', () => {
    it('should update current user with correct parameters', async () => {
      // given
      const props = {
        history: {
          push: () => null,
        },
        updateCurrentUser: jest.fn(),
      }
      jest.spyOn(global.Date, 'now').mockImplementation(() => 1575201600)

      const wrapper = mount(<Typeform {...props} />)

      // when
      await wrapper.instance().onSubmitTypeForm()

      // then
      expect(props.updateCurrentUser).toHaveBeenCalledWith({
        culturalSurveyId: 1,
        culturalSurveyFilledDate: '1970-01-19T05:33:21Z',
        needsToFillCulturalSurvey: false,
      })
    })

    it('should redirect to /bienvenue when request to API is successful', async () => {
      // given
      const props = {
        history: {
          push: jest.fn(),
        },
        updateCurrentUser: () => null,
      }

      const wrapper = mount(<Typeform {...props} />)

      // when
      await wrapper.instance().onSubmitTypeForm()

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
        updateCurrentUser: jest.fn(),
      }

      // when
      const wrapper = mount(<Typeform {...props} />)

      const typeform = wrapper.find('.react-embed-typeform-container')

      // then
      expect(typeform).toHaveLength(1)
    })
  })
})
