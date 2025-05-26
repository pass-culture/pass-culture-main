import { render, screen } from '@testing-library/react'

import { Tag, TagVariant } from './Tag'

describe('Tag', () => {
  it('should always render a label', () => {
    render(<Tag label="Département" />)

    expect(screen.getByText('Département')).toBeInTheDocument()
  })

  it('should render an icon if provided', () => {
    const { container } = render(<Tag label="Département" icon="icon.svg" />)

    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('should not render an icon if not provided', () => {
    const { container } = render(<Tag label="Département" />)

    expect(container.querySelector('svg')).not.toBeInTheDocument()
  })

  it('should not render an icon for new variant', () => {
    const { container } = render(
      <Tag label="Département" variant={TagVariant.NEW} icon="icon.svg" />
    )
    expect(container.querySelector('svg')).not.toBeInTheDocument()
  })

  it.each([TagVariant.BOOKCLUB, TagVariant.HEADLINE, TagVariant.LIKE])(
    'should always render an icon for specific variant: %s',
    (variant) => {
      const { container } = render(
        <Tag label="Département" variant={variant} />
      )

      expect(container.querySelector('svg')).toBeInTheDocument()
    }
  )
})
