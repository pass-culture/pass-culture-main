import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { MemoryRouter, Route } from 'react-router'
import { Link } from 'react-router-dom'

import usePageTitle from 'hooks/usePageTitle'

const PageTitle = (): null => {
  usePageTitle()
  return null
}

describe('useLogPageViewAndSetTitle', () => {
  beforeEach(() => {
    render(
      <MemoryRouter initialEntries={['/accueil']}>
        <PageTitle />
        <Route path="/accueil">
          <span>Main page</span>
          <Link to="/structures">Structures</Link>
        </Route>
        <Route path="/structures">
          <span>Structure page</span>
        </Route>
      </MemoryRouter>
    )
  })
  it('should update page title', async () => {
    const button = screen.getByRole('link', { name: 'Structures' })
    await userEvent.click(button)
    expect(document.title).toEqual(
      'Vos structures juridiques - pass Culture Pro'
    )
  })
})
