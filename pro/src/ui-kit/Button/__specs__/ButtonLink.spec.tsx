import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { renderWithProviders } from 'utils/renderWithProviders'

import { ButtonLink } from '../ButtonLink'

describe('ButtonLink', () => {
  const props = { to: '#', isExternal: true }

  it('should call callback action when clicking the button', async () => {
    const onClick = vi.fn()
    render(
      <ButtonLink {...props} onClick={onClick}>
        test
      </ButtonLink>
    )

    const button = screen.getByRole('link', { name: 'test' })
    await userEvent.click(button)

    expect(onClick).toHaveBeenCalledTimes(1)
    expect(screen.queryByText('Action non disponible')).not.toBeInTheDocument()
  })

  it('should call callback action onblur when clicking outside the button', async () => {
    const onBlur = vi.fn()
    render(
      <ButtonLink {...props} onBlur={onBlur}>
        test
      </ButtonLink>
    )

    const button = screen.getByRole('link', { name: 'test' })
    await userEvent.click(button)
    await userEvent.tab()

    expect(onBlur).toHaveBeenCalledTimes(1)
  })

  it('should enforce absolute links', () => {
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
                      <ButtonLink to="offers">test</ButtonLink>
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
      <ButtonLink {...props} onClick={onClick} isDisabled>
        test
      </ButtonLink>
    )

    const button = screen.getByRole('link', { name: /test/ })
    await userEvent.click(button)

    expect(onClick).not.toHaveBeenCalled()
    expect(screen.getByText('Action non disponible')).toBeInTheDocument()
  })
})
