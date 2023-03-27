import { render, screen } from '@testing-library/react'
import React from 'react'

import SkipLinks from '../SkipLinks'

const renderApp = ({ displayMenu = true } = {}) =>
  render(
    <div>
      <SkipLinks displayMenu={displayMenu} />
      <div id="header-navigation">
        <a href="#">first focusable content element</a>
      </div>
      <div id="content">
        <a href="#">second focusable content element</a>
      </div>
    </div>
  )

describe('SkipLinks', () => {
  it('should not display menu', () => {
    renderApp({ displayMenu: false })
    expect(screen.queryByText('Menu')).not.toBeInTheDocument()
  })
})
