import React from 'react'
import { shallow } from 'enzyme'

import CreditGauge, { computeFillingStep } from '../CreditGauge'
import Icon from '../../../../../layout/Icon/Icon'

const NON_BREAKING_SPACE = '\u00A0'

describe('components | CreditGauge', () => {
  it('should render the gauge picto', () => {
    // Given
    const props = {
      extraClassName: '',
      remainingCredit: 12.0,
      detailsText: 'Some explanations',
      creditLimit: 200,
      picto: 'picto-svg'
    }

    // When
    const wrapper = shallow(<CreditGauge {...props} />)

    // Then
    const picto = wrapper.find(Icon)
    const remainingCredit = wrapper.find({ children: `12${NON_BREAKING_SPACE}€` })
    const detailsText = wrapper.find({ children: 'Some explanations' })
    expect(picto.prop('svg')).toBe('picto-svg')
    expect(remainingCredit).toHaveLength(1)
    expect(detailsText).toHaveLength(1)
  })

  describe('computeFillingStep', () => {
    it('should return step 0 when remainingCredit is between 0 and 9 and creditLimit is 100', () => {
      // Given
      const remainingCredit = 3
      const creditLimit = 100

      // When
      const result = computeFillingStep(remainingCredit, creditLimit)

      // Then
      expect(result).toBe(0)
    })

    it('should return step 5 when remainingCredit is between 50 and 59 and creditLimit is 100', () => {
      // Given
      const remainingCredit = 59
      const creditLimit = 100

      // When
      const result = computeFillingStep(remainingCredit, creditLimit)

      // Then
      expect(result).toBe(5)
    })

    it('should return step 10 when remainingCredit is equal to creditLimit', () => {
      // Given
      const remainingCredit = 100
      const creditLimit = 100

      // When
      const result = computeFillingStep(remainingCredit, creditLimit)

      // Then
      expect(result).toBe(10)
    })
  })
})
