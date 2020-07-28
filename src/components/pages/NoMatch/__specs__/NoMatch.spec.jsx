import React from 'react'
import { mount } from 'enzyme'
import NoMatch from '../NoMatch'
import { MemoryRouter } from 'react-router'
import { NavLink } from 'react-router-dom'

describe('src | components | pages | NoMatch', () => {
  it('should display a message notifying the user they are on a wrong path and a link to home', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <NoMatch />
      </MemoryRouter>
    )

    // then
    const sentence = wrapper.find('.subtitle')
    const link = wrapper.find('.redirection-link')
    const navlink = link.find(NavLink)
    expect(sentence).toHaveLength(1)
    expect(sentence.text()).toBe("Cette page n'existe pas.")
    expect(link).toHaveLength(1)
    expect(navlink).toHaveLength(1)
    expect(navlink.text()).toBe("Retour à la page d'accueil")
  })

  it('should display a link with the redirect props url if not default', () => {
    // when
    const props = {
      redirect: '/mon/autre/url',
    }
    const wrapper = mount(
      <MemoryRouter>
        <NoMatch {...props} />
      </MemoryRouter>
    )

    // then
    const link = wrapper.find('.redirection-link')
    const navlink = link.find(NavLink)
    expect(link).toHaveLength(1)
    expect(navlink).toHaveLength(1)
    expect(navlink.prop('to')).toBe('/mon/autre/url')
  })
})
