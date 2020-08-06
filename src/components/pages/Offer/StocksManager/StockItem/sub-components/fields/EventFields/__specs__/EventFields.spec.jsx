import { shallow } from 'enzyme'
import React from 'react'

import DateField from '../../../../../../../../layout/form/fields/DateField/DateField'
import TimeField from '../../../../../../../../layout/form/fields/TimeField'
import EventFields from '../EventFields'

describe('src | EventFields', () => {
  it('should display a DateField to inform about beginning DateTime', () => {
    // when
    const wrapper = shallow(<EventFields />)

    // then
    const dateField = wrapper.find(DateField)
    expect(dateField).toHaveLength(1)
  })

  it('should display a TimeField to inform about beginning time hour', () => {
    // when
    const wrapper = shallow(<EventFields />)

    // then
    const timeField = wrapper.find(TimeField).findWhere(timeFieldComponent => {
      return timeFieldComponent.props().name === 'beginningTime'
    })
    expect(timeField).toHaveLength(1)
  })
})
