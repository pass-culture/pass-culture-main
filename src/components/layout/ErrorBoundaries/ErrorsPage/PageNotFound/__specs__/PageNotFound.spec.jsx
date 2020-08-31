import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import PageNotFound from '../PageNotFound'

jest.mock('../../../../../../utils/config', () => ({
  ICONS_URL: 'http://path/to/icons',
}))

describe('src | layout | PageNotFound', () => {
  it('should display a message notifying the user they are on a wrong path and add a link to home', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <PageNotFound />
      </MemoryRouter>
    )

    // then
    const image = wrapper.find('img')
    const title = wrapper.find({ children: 'Oh non !' })
    const subtitle = wrapper.find({ children: 'Cette page n’existe pas.' })
    const redirectionLink = wrapper.find('a[href="/"]')
    expect(image.prop('alt')).toBe('')
    expect(image.prop('src')).toBe('http://path/to/icons/404.svg')
    expect(title).toHaveLength(1)
    expect(subtitle).toHaveLength(1)
    expect(redirectionLink).toHaveLength(1)
  })
})
