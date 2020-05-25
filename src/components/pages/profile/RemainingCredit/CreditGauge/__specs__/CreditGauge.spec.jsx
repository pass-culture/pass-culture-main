import { shallow } from 'enzyme'
import React from 'react'

import { NON_BREAKING_SPACE } from '../../../../../../utils/specialCharacters'
import Icon from '../../../../../layout/Icon/Icon'
import CreditGauge from '../CreditGauge'

describe('credit gauge', () => {
  it('should render the gauge picto, remaining credit and some explanations', () => {
    // Given
    const props = {
      extraClassName: '',
      remainingCredit: 12.0,
      creditLimit: 200,
      picto: 'picto-svg',
    }

    // When
    const wrapper = shallow(<CreditGauge {...props}>
      {'Some explanations'}
    </CreditGauge>)

    // Then
    const picto = wrapper.find(Icon)
    const remainingCredit = wrapper.find({ children: `12${NON_BREAKING_SPACE}€` })
    const detailsText = wrapper.find({ children: 'Some explanations' })
    expect(picto.prop('svg')).toBe('picto-svg')
    expect(remainingCredit).toHaveLength(1)
    expect(detailsText).toHaveLength(1)
  })
})
