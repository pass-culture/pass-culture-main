import React from 'react'
import { shallow } from 'enzyme'

import MonPassCulture from '../MonPassCulture'

const walletId = '#profile-wallet-balance-value'
const digitalId = '#profile-digital-wallet-value'
const physicalId = '#profile-physical-wallet-value'
const endValidityDateId = '#profile-end-validity-date'

describe('src | components | MonPassCulture', () => {
  it('should match the snapshot with required props', () => {
    // given
    const props = {
      currentUser: {
        expenses: {
          digital: { actual: 0, max: 200 },
          physical: { actual: 0, max: 200 },
        },
        wallet_balance: 500,
        wallet_date_created: '2019-09-10T08:05:45.778894Z',
      },
    }

    // when
    const wrapper = shallow(<MonPassCulture {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
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
      expect(text).toBe(expected)

      expected = `Jusqu’à 0 € pour les offres numériques`
      text = digitalElement.text()
      expect(digitalElement.text()).toBe(expected)
      expected = `Jusqu’à 0 € pour les biens culturels`

      text = physicalElement.text()
      expect(physicalElement.text()).toBe(expected)
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
      expect(text).toBe(expected)

      expected = `Jusqu’à 90 € pour les offres numériques`
      text = digitalElement.text()
      expect(digitalElement.text()).toBe(expected)
      expected = `Jusqu’à 90 € pour les biens culturels`

      text = physicalElement.text()
      expect(physicalElement.text()).toBe(expected)
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
      expect(text).toBe(expected)

      expected = `Jusqu’à 80 € pour les offres numériques`
      text = digitalElement.text()
      expect(digitalElement.text()).toBe(expected)

      expected = `Jusqu’à 60 € pour les biens culturels`
      text = physicalElement.text()
      expect(physicalElement.text()).toBe(expected)
    })

    it('should render end validity date', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            digital: { actual: 120, max: 200 },
            physical: { actual: 140, max: 200 },
          },
          wallet_balance: 90,
          wallet_date_created: '2019-09-10T08:05:45.778894Z',
        },
      }

      // when
      const wrapper = shallow(<MonPassCulture {...props} />)
      const textWithEndValidityDate = wrapper.find(endValidityDateId).text()

      // then
      expect(textWithEndValidityDate).toBe('Votre crédit est valable jusqu’au 2020 M09 10.')
    })

    it('should not render end validity date when user has no deposit', () => {
      // given
      const props = {
        currentUser: {
          expenses: {
            digital: { actual: 0, max: 200 },
            physical: { actual: 0, max: 200 },
          },
          wallet_balance: 0,
          wallet_date_created: null,
        },
      }

      // when
      const wrapper = shallow(<MonPassCulture {...props} />)
      const wrapperWithEndValidityDate = wrapper.find(endValidityDateId)

      // then
      expect(wrapperWithEndValidityDate).toHaveLength(0)
    })
  })
})
