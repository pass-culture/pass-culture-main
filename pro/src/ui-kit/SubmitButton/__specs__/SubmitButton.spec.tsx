import { render, screen } from '@testing-library/react'
import React from 'react'

import SubmitButton, { SubmitButtonProps } from '../SubmitButton'

const renderSubmitButton = (props: SubmitButtonProps) => {
  return render(<SubmitButton {...props} />)
}

describe('submit button', () => {
  it('should display the text value of the button when is not loading and the button should be enabled', () => {
    // Given
    const props = {
      children: 'Enregistrer',
    }

    // When
    renderSubmitButton(props)

    // Then
    expect(
      screen.getByText('Enregistrer', { selector: 'button' })
    ).toBeEnabled()
  })

  it('should not display the text value of the button when is loading, and the button should be disabled', () => {
    // Given
    const props = {
      isLoading: true,
    }

    // When
    renderSubmitButton(props)

    // Then
    const submitButton = screen.getByRole('button')
    expect(submitButton.textContent).toBe('')
    expect(submitButton).toBeDisabled()
  })
})
