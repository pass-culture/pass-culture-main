import React from 'react'
import { shallow } from 'enzyme'

import RemainingCredit from '../RemainingCredit'
import CreditGauge from '../CreditGauge/CreditGauge'
import Icon from '../../../../layout/Icon/Icon'

const nonBreakingSpace = '\u00A0'

describe('components | RemainingCredit', () => {
  it('should match the snapshot with required props', () => {
    // given
    const props = {
      currentUser: {
        expenses: {
          all: { actual: 10, max: 300 },
          digital: { actual: 0, max: 200 },
          physical: { actual: 0, max: 200 }
        },
        wallet_balance: 500,
        wallet_date_created: '2019-09-10T08:05:45.778894Z'
      }
    }

    // when
    const wrapper = shallow(<RemainingCredit {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should include Crédit restant title', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            all: { actual: 10, max: 300 },
            digital: { actual: 100, max: 200 },
            physical: { actual: 100, max: 200 }
          },
          wallet_balance: 0
        }
      }

      // when
      const wrapper = shallow(<RemainingCredit {...props} />)

      // then
      const title = wrapper.find('h2').text()
      expect(title).toBe('Crédit restant')
    })

    it('should include a title, a money icon and wallet ballance in header', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            all: { actual: 10, max: 300 },
            digital: { actual: 100, max: 200 },
            physical: { actual: 100, max: 200 }
          },
          wallet_balance: 666
        }
      }

      // when
      const wrapper = shallow(<RemainingCredit {...props} />)

      // then
      const moneyPicto = wrapper.find(Icon).first()
      const headerTitle = wrapper.find('h3').first()
      const headerAmount = wrapper.find('p').first()
      const nonBreakingSpace = '\u00A0'
      expect(moneyPicto.prop('svg')).toBe('picto-money')
      expect(headerTitle.text()).toBe('Mon crédit')
      expect(headerAmount.text()).toBe(`666${nonBreakingSpace}€`)
    })

    it('should include three gauges', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            all: { actual: 10, max: 500 },
            digital: { actual: 20, max: 201 },
            physical: { actual: 30, max: 202 }
          },
          wallet_balance: 351
        }
      }

      // when
      const wrapper = shallow(<RemainingCredit {...props} />)

      // then

      const gaugeTitle = wrapper
        .findWhere(
          node => node.text() === `Vous pouvez encore dépenser jusqu’à${nonBreakingSpace}:`
        )
        .first()
      const gauges = wrapper.find(CreditGauge)
      const digitalGauge = gauges.at(0)
      const digitalAmount = digitalGauge.prop('currentAmount')
      const maxDigitalAmount = digitalGauge.prop('maxAmount')
      const physicalGauge = gauges.at(1)
      const physicalAmount = physicalGauge.prop('currentAmount')
      const maxPhysicalAmount = physicalGauge.prop('maxAmount')
      const totalGauge = gauges.at(2)
      const totalAmount = totalGauge.prop('currentAmount')
      const maxTotalAmount = totalGauge.prop('maxAmount')

      expect(gaugeTitle).toHaveLength(1)
      expect(digitalGauge).toHaveLength(1)
      expect(digitalAmount).toBe(181)
      expect(maxDigitalAmount).toBe(201)
      expect(physicalGauge).toHaveLength(1)
      expect(physicalAmount).toBe(172)
      expect(maxPhysicalAmount).toBe(202)
      expect(totalGauge).toHaveLength(1)
      expect(totalAmount).toBe(351)
      expect(maxTotalAmount).toBe(500)
    })

    it('should hide readMore with title and explanation', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            all: { actual: 10, max: 300 },
            digital: { actual: 20, max: 200 },
            physical: { actual: 30, max: 200 }
          },
          wallet_balance: 351
        }
      }

      // when
      const wrapper = shallow(<RemainingCredit {...props} />)

      // then
      const readMoreTitle = wrapper
        .findWhere(
          node =>
            node.text() ===
            `Pourquoi les biens physiques et numériques sont-ils limités${nonBreakingSpace}?`
        )
        .first()
      const readMorePicto = wrapper.find(Icon).at(1)
      const expectedText =
        'Le but du pass Culture est de renforcer vos pratiques culturelles, ' +
        'mais aussi d’en créer de nouvelles. Ces plafonds ont été mis en place ' +
        'pour favoriser la diversification des pratiques culturelles.'
      const readMoreText = wrapper.findWhere(node => node.text() === expectedText).first()
      expect(readMoreTitle).toHaveLength(1)
      expect(readMoreText).toHaveLength(1)
      expect(readMorePicto.prop('svg')).toBe('picto-drop-down')
    })

    it('should render end validity date', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            all: { actual: 10, max: 300 },
            digital: { actual: 120, max: 200 },
            physical: { actual: 140, max: 200 }
          },
          wallet_balance: 90,
          wallet_date_created: '2019-09-10T08:05:45.778894Z'
        }
      }

      // when
      const wrapper = shallow(<RemainingCredit {...props} />)
      
      // then
      const textWithEndValidityDate = wrapper.find('.rc-end-validity-date').text()
      expect(textWithEndValidityDate).toBe('Votre crédit est valable jusqu’au 2021 M09 10.')
    })

    it('should not render end validity date when user has no deposit', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            all: { actual: 10, max: 300 },
            digital: { actual: 0, max: 200 },
            physical: { actual: 0, max: 200 }
          },
          wallet_balance: 0,
          wallet_date_created: null
        }
      }

      // when
      const wrapper = shallow(<RemainingCredit {...props} />)
      const wrapperWithEndValidityDate = wrapper.find('.rc-end-validity-date')

      // then
      expect(wrapperWithEndValidityDate).toHaveLength(0)
    })
  })
})
