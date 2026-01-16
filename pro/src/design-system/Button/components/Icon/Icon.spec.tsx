import { render, screen } from '@testing-library/react'

import { ButtonSize } from '../../types'
import { Icon } from './Icon'

const DEFAULT_ICON_SRC = '/icons/check.svg'

const renderIcon = (props: Partial<Parameters<typeof Icon>[0]> = {}) =>
  render(<Icon icon={DEFAULT_ICON_SRC} {...props} />)

describe('Icon', () => {
  it('should render icon check', () => {
    renderIcon({ iconAlt: 'Check icon' })

    const icon = screen.getByRole('img', { name: 'Check icon' })
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveAttribute('aria-label', 'Check icon')
  })

  it('should render with small size', () => {
    renderIcon({ iconAlt: 'Check icon', size: ButtonSize.SMALL })

    const icon = screen.getByRole('img', { name: 'Check icon' })
    expect(icon).toHaveAttribute('width', '14')
  })

  it('should render with default size', () => {
    renderIcon({ iconAlt: 'Check icon', size: ButtonSize.DEFAULT })

    const icon = screen.getByRole('img', { name: 'Check icon' })
    expect(icon).toHaveAttribute('width', '16')
  })
})
