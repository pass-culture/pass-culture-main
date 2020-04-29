import React from 'react'
import { shallow, mount } from 'enzyme'

import RemainingCredit from '../RemainingCredit'
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
  })
})
