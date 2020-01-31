import React from 'react'
import { shallow } from 'enzyme'

import CreditGauge from '../CreditGauge'
import Icon from '../../../../../layout/Icon/Icon'

describe('components | CreditGauge', () => {
  it('should render the gauge picto', () => {
    // given
    const props = {
      className: '',
      currentAmount: 12.0,
      detailsText: 'Some explanations',
      maxAmount: 200,
      picto: 'picto-svg'
    }

    // when
    const wrapper = shallow(<CreditGauge {...props} />)

    // then
    const picto = wrapper.find(Icon)
    const currentAmount = wrapper.findWhere(node => node.text() === '12').first()
    const detailsText = wrapper.findWhere(node => node.text() === 'Some explanations').first()
    expect(picto.prop('svg')).toBe('picto-svg')
    expect(currentAmount).toHaveLength(1)
    expect(detailsText).toHaveLength(1)
  })

  it('should render an empty gauge when current amount is 0', () => {
    // given
    const props = {
      className: '',
      currentAmount: 0,
      detailsText: 'Some explanations',
      maxAmount: 200,
      picto: 'picto-svg'
    }

    // when
    const wrapper = shallow(<CreditGauge {...props} />)

    // then
    expect(wrapper.state('isGaugeEmpty')).toBe(true)
  })

  it('should render a full gauge when current amount is not 0', () => {
    // given
    const props = {
      className: '',
      detailsText: 'Some explanations',
      picto: 'picto-svg',
      currentAmount: 13,
      maxAmount: 200
    }

    // when
    const wrapper = shallow(<CreditGauge {...props} />)

    // then
    expect(wrapper.state('isGaugeEmpty')).toBe(false)
  })
})
