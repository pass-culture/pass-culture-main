import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import Toggle from '../Toggle'

const renderToggle = props => {
  return render(<Toggle {...props} />)
}

describe('Toggle button', () => {
  it('should display toggle button and should be enabled', () => {
    // Given
    const props = {
      isActive: false,
      isDisabled: false,
      label: 'Label',
    }

    // When
    renderToggle(props)
    const toggleButton = screen.getByRole('button', {})

    // Then
    expect(toggleButton).toBeEnabled()
    expect(toggleButton.textContent).toBe('Label')
  })

  it('should display active / desactive toggle button and should be enabled', async () => {
    // Given
    const props = {
      isActive: false,
      isDisabled: false,
      label: 'Label',
    }

    // When
    renderToggle(props)
    const toggleButton = screen.getByRole('button', {})
    await userEvent.click(toggleButton)

    // Then
    expect(toggleButton).toBeEnabled()
    expect(toggleButton.textContent).toBe('Label')
    expect(toggleButton.getAttribute('aria-pressed')).toBe('true')

    await userEvent.click(toggleButton)

    expect(toggleButton).toBeEnabled()
    expect(toggleButton.textContent).toBe('Label')
    expect(toggleButton.getAttribute('aria-pressed')).toBe('false')
  })

  it('should not display active toggle button when should be disabled', async () => {
    // Given
    const props = {
      isActive: false,
      isDisabled: true,
      label: 'Label',
    }

    // When
    renderToggle(props)
    const toggleButton = screen.getByRole('button', {})
    await userEvent.click(toggleButton)

    // Then
    expect(toggleButton).toBeDisabled()
    expect(toggleButton.textContent).toBe('Label')
    expect(toggleButton.getAttribute('aria-pressed')).toBe('false')
  })

  it('should use callback function onclick', async () => {
    // Given
    let counter = 0
    const addToCounter = jest.fn(() => counter++)
    const props = {
      handleClick: addToCounter,
    }

    // When
    renderToggle(props)
    const toggleButton = screen.getByRole('button', {})
    await userEvent.click(toggleButton)

    // Then
    expect(addToCounter).toHaveBeenCalledTimes(1)
    expect(counter).toEqual(1)
  })
})
