import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import ButtonLink from '../ButtonLink'

describe('ButtonLink', () => {
  const props = { to: '#', isExternal: true }

  it('should call callback action when clicking the button', async () => {
    const onClick = jest.fn()
    render(
      <ButtonLink link={props} onClick={onClick}>
        test
      </ButtonLink>
    )

    const button = screen.getByRole('link', { name: 'test' })
    await userEvent.click(button)

    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('should not call callback action when button disabled', async () => {
    const onClick = jest.fn()
    render(
      <ButtonLink link={props} onClick={onClick} isDisabled>
        test
      </ButtonLink>
    )

    const button = screen.getByRole('link', { name: 'test' })
    await userEvent.click(button)

    expect(onClick).not.toHaveBeenCalled()
  })

  it('should display tooltip', () => {
    render(
      <ButtonLink link={props} hasTooltip>
        test
      </ButtonLink>
    )
    expect(screen.getByTestId('tooltip')).toBeInTheDocument()
  })
})
