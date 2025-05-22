import { render, screen } from '@testing-library/react'

import { Button, ButtonProps } from '../Button'

const renderButton = (props: ButtonProps = {}) => {
  return render(<Button {...props}>Enregistrer</Button>)
}

describe('submit button', () => {
  it('should display the text value of the button when is not loading and the button should be enabled', () => {
    renderButton()

    expect(
      screen.getByText('Enregistrer', { selector: 'button' })
    ).toBeEnabled()
  })

  it('should disable the button when is loading', () => {
    renderButton({ isLoading: true })

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })
})
