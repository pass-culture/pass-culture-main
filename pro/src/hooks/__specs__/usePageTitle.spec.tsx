import '@testing-library/jest-dom'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router'
import { Link } from 'react-router-dom'

import usePageTitle from 'hooks/usePageTitle'
import { renderWithProviders } from 'utils/renderWithProviders'

const PageTitle = (): null => {
  usePageTitle()
  return null
}

describe('usePageTitle', () => {
  beforeEach(() => {
    renderWithProviders(
      <Routes>
        <Route
          path="/accueil"
          element={
            <>
              <PageTitle />
              <span>Main page</span>
              <Link to="/structures">Structures</Link>
            </>
          }
        />
        <Route
          path="/structures"
          element={
            <>
              <PageTitle />
              <span>Structure page</span>
            </>
          }
        />
      </Routes>,
      { initialRouterEntries: ['/accueil'] }
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
