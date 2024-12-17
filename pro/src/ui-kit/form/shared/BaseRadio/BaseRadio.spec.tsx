import { render, screen } from '@testing-library/react'

import { BaseRadio, BaseRadioProps } from './BaseRadio'

const props: BaseRadioProps = {
  label: 'My radio input label',
  checked: true,
  onChange: () => {},
}

describe('BaseRadio', () => {
  it('should display a radio input', () => {
    render(<BaseRadio {...props} />)

    expect(
      screen.getByRole('radio', { name: 'My radio input label' })
    ).toBeInTheDocument()
  })

  it('should display an invalid radio input', () => {
    render(<BaseRadio {...props} hasError />)

    expect(
      screen.getByRole('radio', { name: 'My radio input label' })
    ).toHaveAttribute('aria-invalid', 'true')
  })

  it('should display radio input children when the input is checked', () => {
    render(<BaseRadio {...props} childrenOnChecked={<div>My children</div>} />)

    expect(screen.getByText('My children')).toBeInTheDocument()
  })

  it('should not display radio input children when the input is unchecked', () => {
    render(
      <BaseRadio
        {...props}
        childrenOnChecked={<div>My children</div>}
        checked={false}
      />
    )

    expect(screen.queryByText('My children')).not.toBeInTheDocument()
  })
})
