import { shallow } from 'enzyme'
import React from 'react'

import { NON_BREAKING_SPACE } from '../../../../../utils/specialCharacters'
import Header from '../Header'
import User from '../../ValueObjects/User'

describe('profileHeader', () => {
  let props

  beforeEach(() => {
    props = {
      user: new User({
        publicName: 'Rosa Bonheur',
        wallet_balance: 153,
        deposit_expiration_date: '2020-12-23T09:00:00.000000Z',
      }),
    }
  })

  it('should display my pseudo, my wallet balance and my end validity date', () => {
    // When
    const wrapper = shallow(<Header {...props} />)

    // Then
    const pseudo = wrapper.find({ children: 'Rosa Bonheur' })
    const walletBalance = wrapper.find({ children: `153${NON_BREAKING_SPACE}€` })
    const endValidityDate = wrapper.find({ children: 'crédit valable jusqu’au 23/12/2020' })
    expect(pseudo).toHaveLength(1)
    expect(walletBalance).toHaveLength(1)
    expect(endValidityDate).toHaveLength(1)
  })

  it('should not end validity date when user is not a beneficiary', () => {
    // When
    props.user = new User({ isBeneficiary: false })
    const wrapper = shallow(<Header {...props} />)

    // Then
    const endValidityDate = wrapper.find('.ph-end-validity-date')
    expect(endValidityDate).toHaveLength(0)
  })
})
