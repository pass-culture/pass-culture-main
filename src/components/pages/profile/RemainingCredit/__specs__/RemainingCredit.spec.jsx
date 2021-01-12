import React from 'react'
import { shallow, mount } from 'enzyme'

import RemainingCredit from '../RemainingCredit'
import { NON_BREAKING_SPACE } from '../../../../../utils/specialCharacters'
import User from '../../ValueObjects/User'
import CreditGauge from '../CreditGauge/CreditGauge'

describe('remainingCredit', () => {
  let props

  beforeEach(() => {
    props = {
      user: new User({
        deposit_version: 1,
        expenses: [
          { domain: 'all', current: 10, limit: 500 },
          { domain: 'digital', current: 20, limit: 201 },
          { domain: 'physical', current: 30, limit: 202 },
        ],
        wallet_balance: 351,
      }),
    }
  })

  describe('render', () => {
    it('should fill the gauge with the right values', () => {
      // When
      const wrapper = shallow(<RemainingCredit {...props} />)

      // Then
      const gauges = wrapper.find(CreditGauge)
      expect(gauges).toHaveLength(3)

      const digitalGauge = gauges.find({ extraClassName: 'gauge-digital' })
      expect(digitalGauge.prop('creditLimit')).toBe(201)

      const physicalGauge = gauges.find({ extraClassName: 'gauge-physical' })
      expect(physicalGauge.prop('creditLimit')).toBe(202)

      const allGauge = gauges.find({ extraClassName: 'gauge-total' })
      expect(allGauge.prop('creditLimit')).toBe(500)
    })

    it('should display an empty account when no deposit', () => {
      // Given
      props.user = new User({
        expenses: [],
        wallet_balance: 0,
      })

      // When
      const wrapper = mount(<RemainingCredit {...props} />)

      // Then
      const digitalGauge = wrapper.find('.gauge-digital')
      expect(digitalGauge).toHaveLength(1)
      expect(digitalGauge.text()).toBe('0 €en offres\n' + 'numériques\n' + '(streaming…)')

      const physicalGauge = wrapper.find('.gauge-physical')
      expect(physicalGauge).toHaveLength(1)
      expect(physicalGauge.text()).toBe('0 €en offres\n' + 'physiques\n' + '(livres…)')

      const totalGauge = wrapper.find('.gauge-total')
      expect(totalGauge).toHaveLength(1)
      expect(totalGauge.text()).toBe('0 €en sorties\n' + '(spectacles…)')
    })

    it('should display three gauges and prices', () => {
      // When
      const wrapper = mount(<RemainingCredit {...props} />)

      // Then
      const digitalRemainingCredit = wrapper.find({ children: `181${NON_BREAKING_SPACE}€` })
      const physicalRemainingCredit = wrapper.find({ children: `172${NON_BREAKING_SPACE}€` })
      expect(digitalRemainingCredit).toHaveLength(1)
      expect(physicalRemainingCredit).toHaveLength(1)
    })

    it('should display details text', () => {
      // When
      const wrapper = shallow(<RemainingCredit {...props} />)

      // Then
      const gaugeTitle = wrapper.find({
        children: `Tu peux encore dépenser jusqu’à${NON_BREAKING_SPACE}:`,
      })
      const digitalRemainingCreditText = wrapper.find({
        children: `en offres\u000Anumériques\u000A(streaming…)`,
      })
      const physicalRemainingCreditText = wrapper.find({
        children: 'en offres\u000Aphysiques\u000A(livres…)',
      })
      const remainingCreditText = wrapper.find({ children: 'en sorties\u000A(spectacles…)' })
      expect(gaugeTitle).toHaveLength(1)
      expect(digitalRemainingCreditText).toHaveLength(1)
      expect(physicalRemainingCreditText).toHaveLength(1)
      expect(remainingCreditText).toHaveLength(1)
    })

    describe('readMore', () => {
      const READ_MORE_TEXT = `Le but du pass Culture est de renforcer tes pratiques culturelles,
                mais aussi d’en créer de nouvelles. Ces plafonds ont été mis en place
                pour favoriser la diversification des pratiques culturelles.`

      it('should render hidden readMore explanation', () => {
        // When
        const wrapper = shallow(<RemainingCredit {...props} />)

        // Then
        const readMoreExplanationNode = wrapper.find({ children: READ_MORE_TEXT })
        expect(readMoreExplanationNode).toHaveLength(0)
      })

      it('should display readMore explanation on title click', () => {
        // When
        const wrapper = shallow(<RemainingCredit {...props} />)
        const readMoreTitle = `Pourquoi les biens physiques et numériques sont-ils limités${NON_BREAKING_SPACE}?`
        const readMoreTitleNode = wrapper.find({ children: readMoreTitle })
        readMoreTitleNode.invoke('onClick')()

        // Then
        const readMoreExplanationNode = wrapper.find({ children: READ_MORE_TEXT })

        expect(readMoreExplanationNode).toHaveLength(1)
      })
    })
  })
})
