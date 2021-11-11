import React from 'react'
import { mount } from 'enzyme'

import Typeform from '../Typeform'

jest.mock('uuid/v1', () => {
  return () => 'fakeUUID'
})

const props = {
  history: {
    push: jest.fn(),
  },
  updateCurrentUser: jest.fn(),
  userId: 1234,
}

describe('src | components | pages | typeform | Typeform', () => {
  afterEach(jest.clearAllMocks)

  it('should display typeform DOM container', () => {
    // given
    const wrapper = mount(<Typeform {...props} />)

    // then
    const typeform = wrapper.find('.react-embed-typeform-container')
    expect(typeform).toHaveLength(1)
  })

  it('should update current user with correct parameters on typeform submit', async () => {
    // given
    jest.spyOn(global.Date, 'now').mockReturnValue(1575201600)
    const wrapper = mount(<Typeform {...props} />)

    // when
    await wrapper.instance().onSubmitTypeform()

    // then
    expect(props.updateCurrentUser).toHaveBeenCalledWith({
      culturalSurveyId: 'fakeUUID',
      culturalSurveyFilledDate: '1970-01-19T05:33:21Z',
      needsToFillCulturalSurvey: false,
    })
  })

  it('should redirect to /bienvenue after successful user profile update when typeform is submitted', async () => {
    // given
    const wrapper = mount(<Typeform {...props} />)

    // when
    await wrapper.instance().onSubmitTypeform()

    // then
    expect(props.history.push).toHaveBeenCalledWith('/bienvenue')
  })
})
