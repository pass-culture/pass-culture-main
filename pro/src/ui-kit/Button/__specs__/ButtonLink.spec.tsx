import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { renderWithProviders } from 'utils/renderWithProviders'

import ButtonLink from '../ButtonLink'

describe('ButtonLink', () => {
  const props = { to: '#', isExternal: true }

  it('should call callback action when clicking the button', async () => {
    const onClick = vi.fn()
    render(
      <ButtonLink link={props} onClick={onClick}>
        test
      </ButtonLink>
    )

    const button = screen.getByRole('link', { name: 'test' })
    await userEvent.click(button)

    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('should enforce absolute links', async () => {
    renderWithProviders(
      <Routes>
        <Route
          path="/offers/*"
          element={
            <>
              <div>offers</div>
              <Routes>
                <Route
                  path="subrouter"
                  element={
                    <div>
                      sub route{' '}
                      {/* here the link is missing the starting slash to be an absolute link */}
                      <ButtonLink link={{ to: 'offers', isExternal: false }}>
                        test
                      </ButtonLink>
                    </div>
                  }
                />
              </Routes>
            </>
          }
        />
      </Routes>,
      { initialRouterEntries: ['/offers/subrouter'] }
    )

    const button = screen.getByRole('link', { name: 'test' })
    // the rendered link is absolute
    expect(button).toHaveAttribute('href', '/offers')
  })

  it('should not call callback action when button disabled', async () => {
    const onClick = vi.fn()
    render(
      <ButtonLink link={props} onClick={onClick} isDisabled>
        test
      </ButtonLink>
    )

    const button = screen.getByRole('link', { name: 'test' })
    await userEvent.click(button)

    expect(onClick).not.toHaveBeenCalled()
  })
})
