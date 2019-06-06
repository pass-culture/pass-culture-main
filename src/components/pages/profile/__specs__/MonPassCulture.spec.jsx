// jest --env=jsdom ./src/components/pages/profile/tests/MonPassCulture --watch
import React from 'react'
import { shallow } from 'enzyme'

import MonPassCulture from '../MonPassCulture'

const walletId = '#profile-wallet-balance-value'
const digitalId = '#profile-digital-wallet-value'
const physicalId = '#profile-physical-wallet-value'

describe('src | components | MonPassCulture', () => {
  describe('snapshot', () => {
    it('should match snapshot with required props', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            digital: { actual: 0, max: 200 },
            physical: { actual: 0, max: 200 },
          },
          wallet_balance: 500,
        },
      }

      // when
      const wrapper = shallow(<MonPassCulture {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    it('with wallet value set to 0', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            digital: { actual: 100, max: 200 },
            physical: { actual: 100, max: 200 },
          },
          wallet_balance: 0,
        },
      }

      // when
      const wrapper = shallow(<MonPassCulture {...props} />)
      const walletElement = wrapper.find(walletId)
      const digitalElement = wrapper.find(digitalId)
      const physicalElement = wrapper.find(physicalId)

      // then
      let expected = `Il reste 0 €`
      let text = walletElement.text()
      expect(text).toEqual(expected)

      expected = `Jusqu'à 0 € pour les offres numériques`
      text = digitalElement.text()
      expect(digitalElement.text()).toEqual(expected)
      expected = `Jusqu'à 0 € pour les biens culturels`

      text = physicalElement.text()
      expect(physicalElement.text()).toEqual(expected)
    })
    it('with wallet value set to 90', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            digital: { actual: 20, max: 200 },
            physical: { actual: 80, max: 200 },
          },
          wallet_balance: 90,
        },
      }

      // when
      const wrapper = shallow(<MonPassCulture {...props} />)
      const walletElement = wrapper.find(walletId)
      const digitalElement = wrapper.find(digitalId)
      const physicalElement = wrapper.find(physicalId)

      // then
      let expected = `Il reste 90 €`
      let text = walletElement.text()
      expect(text).toEqual(expected)

      expected = `Jusqu'à 90 € pour les offres numériques`
      text = digitalElement.text()
      expect(digitalElement.text()).toEqual(expected)
      expected = `Jusqu'à 90 € pour les biens culturels`

      text = physicalElement.text()
      expect(physicalElement.text()).toEqual(expected)
    })
    it('render with wallet value set to 200', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            digital: { actual: 120, max: 200 },
            physical: { actual: 140, max: 200 },
          },
          wallet_balance: 200,
        },
      }

      // when
      const wrapper = shallow(<MonPassCulture {...props} />)
      const walletElement = wrapper.find(walletId)
      const digitalElement = wrapper.find(digitalId)
      const physicalElement = wrapper.find(physicalId)

      // then
      let expected = `Il reste 200 €`
      let text = walletElement.text()
      expect(text).toEqual(expected)

      expected = `Jusqu'à 80 € pour les offres numériques`
      text = digitalElement.text()
      expect(digitalElement.text()).toEqual(expected)

      expected = `Jusqu'à 60 € pour les biens culturels`
      text = physicalElement.text()
      expect(physicalElement.text()).toEqual(expected)
    })
    it('render with invalid wallet balance', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            digital: { actual: 120, max: 200 },
            physical: { actual: 140, max: 200 },
          },
          wallet_balance: null,
        },
      }

      // when
      const wrapper = shallow(<MonPassCulture {...props} />)
      const walletElement = wrapper.find(walletId)
      const digitalElement = wrapper.find(digitalId)
      const physicalElement = wrapper.find(physicalId)

      // then
      let expected = `Il reste -- €`
      let text = walletElement.text()
      expect(text).toEqual(expected)

      expected = `Jusqu'à -- € pour les offres numériques`
      text = digitalElement.text()
      expect(text).toEqual(expected)

      expected = `Jusqu'à -- € pour les biens culturels`
      text = physicalElement.text()
      expect(text).toEqual(expected)
    })
  })
})
