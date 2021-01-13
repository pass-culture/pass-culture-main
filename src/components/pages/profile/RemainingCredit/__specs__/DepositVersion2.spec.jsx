import React from 'react'
import { shallow, mount } from 'enzyme'

import { NON_BREAKING_SPACE } from '../../../../../utils/specialCharacters'
import User from '../../ValueObjects/User'
import CreditGauge from '../CreditGauge/CreditGauge'
import DepositVersion2 from '../DepositVersion2'

describe('depositVersion2', () => {
  let props

  it('should display an empty account when no deposit', () => {
    // Given
    props = {
      user: new User({
        expenses: [],
        wallet_balance: 0,
      }),
    }

    // When
    const wrapper = mount(<DepositVersion2 {...props} />)

    // Then
    const digitalGauge = wrapper.find('.gauge-digital')
    expect(digitalGauge).toHaveLength(1)
    expect(digitalGauge.text()).toBe('0 €en offres\n' + 'numériques\n' + '(streaming…)')

    const totalGauge = wrapper.find('.gauge-total')
    expect(totalGauge).toHaveLength(1)
    expect(totalGauge.text()).toBe(
      '0 €en sorties et\n' + 'biens physiques\n' + '(concerts, livres…)'
    )
  })

  describe('when is only limited to digital', () => {
    beforeEach(() => {
      props = {
        user: new User({
          deposit_version: 2,
          expenses: [
            { domain: 'all', current: 9, limit: 300 },
            { domain: 'digital', current: 20, limit: 100 },
          ],
          wallet_balance: 271,
        }),
      }
    })

    it('should display two gauges', () => {
      // When
      const wrapper = shallow(<DepositVersion2 {...props} />)

      // Then
      const gauges = wrapper.find(CreditGauge)
      expect(gauges).toHaveLength(2)
      expect(gauges.exists({ extraClassName: 'gauge-digital' })).toBe(true)
      expect(gauges.exists({ extraClassName: 'gauge-total' })).toBe(true)
    })

    it('should fill the gauge with the right values', () => {
      // When
      const wrapper = shallow(<DepositVersion2 {...props} />)

      // Then
      const gauges = wrapper.find(CreditGauge)

      const digitalGauge = gauges.find({ extraClassName: 'gauge-digital' })
      expect(digitalGauge.prop('creditLimit')).toBe(100)

      const allGauge = gauges.find({ extraClassName: 'gauge-total' })
      expect(allGauge.prop('creditLimit')).toBe(300)
    })

    it('should display remaining total and digital prices', () => {
      // When
      const wrapper = mount(<DepositVersion2 {...props} />)

      // Then
      const digitalGauge = wrapper.find(CreditGauge).find({ extraClassName: 'gauge-digital' })
      expect(digitalGauge.text()).toBe('80 €en offres\n' + 'numériques\n' + '(streaming…)')

      const allGauge = wrapper.find(CreditGauge).find({ extraClassName: 'gauge-total' })
      expect(allGauge.text()).toBe(
        '271 €en sorties et\n' + 'biens physiques\n' + '(concerts, livres…)'
      )
    })

    it('should display deposit summary', () => {
      // When
      const wrapper = shallow(<DepositVersion2 {...props} />)

      // Then
      const gaugeTitle = wrapper.find({
        children: `Tu peux encore dépenser jusqu’à${NON_BREAKING_SPACE}:`,
      })
      expect(gaugeTitle).toHaveLength(1)
    })

    describe('readMore', () => {
      const READ_MORE_TEXT = `Le but du pass Culture est de renforcer tes pratiques culturelles,
                mais aussi d’en créer de nouvelles. Ces plafonds ont été mis en place
                pour favoriser la diversification des pratiques culturelles.`

      it('should render hidden readMore explanation', () => {
        // When
        const wrapper = shallow(<DepositVersion2 {...props} />)

        // Then
        const readMoreExplanationNode = wrapper.find({ children: READ_MORE_TEXT })
        expect(readMoreExplanationNode).toHaveLength(0)
      })

      it('should display readMore explanation on title click', () => {
        // When
        const wrapper = shallow(<DepositVersion2 {...props} />)
        const readMoreTitle = `Pourquoi les biens numériques sont-ils limités${NON_BREAKING_SPACE}?`
        const readMoreTitleNode = wrapper.find({ children: readMoreTitle })
        readMoreTitleNode.invoke('onClick')()

        // Then
        const readMoreExplanationNode = wrapper.find({ children: READ_MORE_TEXT })

        expect(readMoreExplanationNode).toHaveLength(1)
      })
    })
  })
})
