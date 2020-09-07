import { mount } from 'enzyme'
import React from 'react'

import { NON_BREAKING_SPACE } from '../../../../../../utils/specialCharacters'
import Header from '../Header'
import User from '../../ValueObjects/User'
import { Link } from 'react-router-dom'
import { MemoryRouter } from 'react-router'
import Icon from '../../../../../layout/Icon/Icon'

describe('profileHeader', () => {
  let props

  beforeEach(() => {
    props = {
      user: new User({
        publicName: 'Rosa Bonheur',
        wallet_balance: 153,
        wallet_date_created: '2018-12-23T09:07:48.914901Z',
      }),
    }
  })

  it('should display my pseudo, my wallet balance and my end validity date', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <Header {...props} />
      </MemoryRouter>,
    )

    // Then
    const pseudo = wrapper.find({ children: 'Rosa Bonheur' })
    const walletBalance = wrapper.find({ children: `153${NON_BREAKING_SPACE}€` })
    const endValidityDate = wrapper.find({ children: 'crédit valable jusqu’au 23/12/2020' })
    expect(pseudo).toHaveLength(1)
    expect(walletBalance).toHaveLength(1)
    expect(endValidityDate).toHaveLength(1)
  })

  it('should display a back button to homepage', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <Header {...props} />
      </MemoryRouter>,
    )

    // then
    const link = wrapper.find(Link)
    expect(link).toHaveLength(1)
    expect(link.prop('to')).toBe('/accueil')
    const icon = link.find(Icon)
    expect(icon).toHaveLength(1)
    expect(icon.prop('svg')).toBe('ico-arrow-previous')
  })
})
