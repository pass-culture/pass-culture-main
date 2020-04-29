import React from 'react'
import { shallow, mount } from 'enzyme'

import RemainingCredit from '../RemainingCredit'
import Icon from '../../../../layout/Icon/Icon'
import { NON_BREAKING_SPACE } from '../../../../../utils/specialCharacters'

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
      const wrapper = mount(<RemainingCredit {...props} />)

      // Then
      const gaugeTitle = wrapper.find({
        children: `Tu peux encore dépenser jusqu’à${NON_BREAKING_SPACE}:`,
      })

      const digitalRemainingCredit = wrapper.find({ children: `181${NON_BREAKING_SPACE}€` })
      const physicalRemainingCredit = wrapper.find({ children: `172${NON_BREAKING_SPACE}€` })
      const remainingCredit = wrapper.find({ children: `351${NON_BREAKING_SPACE}€` })

      const digitalRemainingCreditText = wrapper.find({
        children: 'en offres numériques (streaming…)',
      })
      const physicalRemainingCreditText = wrapper.find({
        children: 'en offres physiques (livres…)',
      })
      const remainingCreditText = wrapper.find({ children: 'en sorties (spectacles…)' })

      expect(gaugeTitle).toHaveLength(1)

      expect(digitalRemainingCredit).toHaveLength(1)
      expect(physicalRemainingCredit).toHaveLength(1)
      expect(remainingCredit).toHaveLength(2)

      expect(digitalRemainingCreditText).toHaveLength(1)
      expect(physicalRemainingCreditText).toHaveLength(1)
      expect(remainingCreditText).toHaveLength(1)
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
