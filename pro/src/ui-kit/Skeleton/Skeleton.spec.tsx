import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { Skeleton } from './Skeleton'

describe('Skeleton Component', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(<Skeleton />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should apply custom height and width styles', () => {
    render(<Skeleton height="50px" width="200px" />)

    const skeleton = screen.getByTestId('skeleton')
    expect(skeleton).toHaveStyle('height: 50px')
    expect(skeleton).toHaveStyle('width: 200px')
  })

  it('should apply rounded-full class when roundedFull prop is true', () => {
    render(<Skeleton roundedFull={true} />)

    const skeleton = screen.getByTestId('skeleton')
    expect(skeleton).toHaveClass('rounded-full')
  })

  it('should not apply rounded-full class when roundedFull prop is false', () => {
    render(<Skeleton roundedFull={false} />)

    const skeleton = screen.getByTestId('skeleton')
    expect(skeleton).not.toHaveClass('rounded-full')
  })

  it('should render the visually hidden text', () => {
    render(<Skeleton />)

    const hiddenText = screen.getByText('Chargement en cours')
    expect(hiddenText).toBeInTheDocument()
    expect(hiddenText).toHaveClass('visually-hidden')
  })
})
