import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import NotFound from '../NotFound'

describe('src | components | pages | NotFound', () => {
  it('should display a message notifying the user they are on a wrong path and add a link to home', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <NotFound />
      </MemoryRouter>
    )

    // then
    const title = wrapper.find({ children: 'Oh non !' })
    const subtitle = wrapper.find({ children: 'Cette page n’existe pas.' })
    const redirectionLink = wrapper.find('a[href="/accueil"]')

    expect(title).toHaveLength(1)
    expect(subtitle).toHaveLength(1)
    expect(redirectionLink).toHaveLength(1)
  })

  it('should display a link with the redirect props url if not default', () => {
    // when
    const props = {
      redirect: '/mon/autre/url',
    }
    const wrapper = mount(
      <MemoryRouter>
        <NotFound {...props} />
      </MemoryRouter>
    )

    // then
    const redirectionLink = wrapper.find('a[href="/mon/autre/url"]')

    expect(redirectionLink).toHaveLength(1)
  })
})
