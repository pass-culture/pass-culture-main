import React from 'react'
import { shallow, mount } from 'enzyme'
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
        needsToFillCulturalSurvey: false,
      }

      const wrapper = shallow(<Typeform {...props} />)
      const historyPush = jest.spyOn(props.history, 'push')

      // when
      wrapper.instance().onSubmitTypeForm()

      // then
      expect(historyPush).toHaveBeenCalledWith('/bienvenue')
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
