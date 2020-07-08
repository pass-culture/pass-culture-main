import { mount } from 'enzyme'
import React from 'react'
import Home from '../Home'
import { Link } from 'react-router-dom'
import { MemoryRouter } from 'react-router'
import Icon from '../../../layout/Icon/Icon'

describe('src | components | Home', () => {
  let props

  beforeEach(() => {
    props = {
      user: {
        publicName: 'Iron Man',
        wallet_balance: 200.1
      }
    }
  })

  it('should render a Link component with the profil icon', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <Home {...props} />
      </MemoryRouter>
    )

    // then
    const link = wrapper.find(Link)
    expect(link).toHaveLength(1)
    expect(link.prop('to')).toBe('/profil')

    const icon = link.find(Icon)
    expect(icon).toHaveLength(1)
    expect(icon.prop('svg')).toBe('ico-informations-white')
  })

  it('should render a title with the user public name', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <Home {...props} />
      </MemoryRouter>
    )

    // then
    const title = wrapper.find({ children: 'Bonjour Iron Man'})
    expect(title).toHaveLength(1)
  })

  it('should render a subtile with the user wallet balance', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <Home {...props} />
      </MemoryRouter>
    )

    // then
    const title = wrapper.find({ children: 'Tu as 200,1€ sur ton pass'})
    expect(title).toHaveLength(1)
  })
})
