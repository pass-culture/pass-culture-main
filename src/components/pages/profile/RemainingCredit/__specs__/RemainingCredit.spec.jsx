import React from 'react'
import { shallow } from 'enzyme'

import RemainingCredit from '../RemainingCredit'
import CreditGauge from '../CreditGauge/CreditGauge'
import Icon from '../../../../layout/Icon/Icon'

const NON_BREAKING_SPACE = '\u00A0'

const READ_MORE_TEXT = `Le but du pass Culture est de renforcer vos pratiques culturelles,
                mais aussi d’en créer de nouvelles. Ces plafonds ont été mis en place
                pour favoriser la diversification des pratiques culturelles.`

describe('components | RemainingCredit', () => {
  let props

  beforeEach(() => {
    props = {
      currentUser: {
        expenses: {
          all: { actual: 10, max: 300 },
          digital: { actual: 100, max: 200 },
          physical: { actual: 100, max: 200 },
        },
        wallet_balance: 0,
      },
    }
  })

  describe('render', () => {
    it('should include Crédit restant title', () => {
      // When
      const wrapper = shallow(<RemainingCredit {...props} />)

      // Then
      const title = wrapper.find('h2').text()
      expect(title).toBe('Crédit restant')
    })

    it('should include a title, a money icon and wallet ballance in header', () => {
      // Given
      props.currentUser.wallet_balance = 666

      // When
      const wrapper = shallow(<RemainingCredit {...props} />)

      // Then
      const moneyPicto = wrapper.find(Icon).first()
      const headerTitle = wrapper.find({ children: 'Mon crédit' })
      const headerRemainingCredit = wrapper.find('p').first()
      expect(moneyPicto.prop('svg')).toBe('picto-money')
      expect(headerTitle).toHaveLength(1)
      expect(headerRemainingCredit.text()).toBe(`666${NON_BREAKING_SPACE}€`)
    })

    it('should include three gauges', () => {
      // Given
      props.currentUser = {
        expenses: {
          all: { actual: 10, max: 500 },
          digital: { actual: 20, max: 201 },
          physical: { actual: 30, max: 202 },
        },
        wallet_balance: 351,
      }

      // When
      const wrapper = shallow(<RemainingCredit {...props} />)

      // Then
      const gaugeTitle = wrapper.find({
        children: `Vous pouvez encore dépenser jusqu’à${NON_BREAKING_SPACE}:`,
      })

      const gauges = wrapper.find(CreditGauge)
      const digitalGauge = gauges.at(0)
      const physicalGauge = gauges.at(1)
      const initialDepositGauge = gauges.at(2)

      const digitalRemainingCredit = digitalGauge.prop('remainingCredit')
      const physicalRemainingCredit = physicalGauge.prop('remainingCredit')
      const remainingCredit = initialDepositGauge.prop('remainingCredit')

      const digitalCreditLimit = digitalGauge.prop('creditLimit')
      const physicalCreditLimit = physicalGauge.prop('creditLimit')
      const initialDeposit = initialDepositGauge.prop('creditLimit')

      expect(gaugeTitle).toHaveLength(1)
      expect(digitalGauge).toHaveLength(1)
      expect(physicalGauge).toHaveLength(1)
      expect(initialDepositGauge).toHaveLength(1)

      expect(digitalRemainingCredit).toBe(181)
      expect(physicalRemainingCredit).toBe(172)
      expect(remainingCredit).toBe(351)

      expect(digitalCreditLimit).toBe(201)
      expect(physicalCreditLimit).toBe(202)
      expect(initialDeposit).toBe(500)
    })

    describe('readMore', () => {
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
        readMoreTitleNode.simulate('click')

        // Then
        const readMoreExplanationNode = wrapper.find({ children: READ_MORE_TEXT })

        expect(readMoreExplanationNode).toHaveLength(1)
      })
    })

    it('should render end validity date', () => {
      // Given
      props.currentUser.wallet_date_created = '2019-09-10T08:05:45.778894Z'

      // When
      const wrapper = shallow(<RemainingCredit {...props} />)

      // Then
      const textWithEndValidityDate = wrapper.find('.rc-end-validity-date').text()
      expect(textWithEndValidityDate).toBe('Votre crédit est valable jusqu’au 10 septembre 2021.')
    })

    it('should not render end validity date when user has no deposit', () => {
      // Given
      props.currentUser.wallet_date_created = null

      // When
      const wrapper = shallow(<RemainingCredit {...props} />)
      const wrapperWithEndValidityDate = wrapper.find('.rc-end-validity-date')

      // Then
      expect(wrapperWithEndValidityDate).toHaveLength(0)
    })
  })
})
