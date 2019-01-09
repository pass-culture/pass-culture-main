// jest --env=jsdom ./src/components/pages/tests/BetaPage --watch
import React from 'react'
import { render } from 'enzyme'
import { MemoryRouter } from 'react-router-dom'

import { RawBetaPage } from '../BetaPage'

describe('src | components | pages | RawBetaPage', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = render(
      <MemoryRouter initialEntries={['/beta']}>
        <RawBetaPage />
      </MemoryRouter>
    )
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('should contains a link to connexion page', () => {
    // when
    const wrapper = render(
      <MemoryRouter initialEntries={['/beta']}>
        <RawBetaPage />
      </MemoryRouter>
    )
    const element = wrapper.find('#beta-connexion-link')
    // then
    expect(element).toHaveLength(1)
    expect(element.prop('href')).toEqual('/connexion')
  })
})
