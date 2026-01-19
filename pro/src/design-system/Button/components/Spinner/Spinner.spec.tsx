import { render, screen } from '@testing-library/react'

import { Spinner } from './Spinner'

const renderSpinner = (props = {}) => {
  return render(<Spinner {...props} />)
}

describe('Spinner', () => {
  it('should render the spinner icon', () => {
    renderSpinner()

    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })
})
