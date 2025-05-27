import { render, screen } from '@testing-library/react'

import { Tag, TagProps, TagVariant } from './Tag'

function renderTag(props: TagProps) {
  return render(<Tag {...props} />)
}

describe('Tag', () => {
  it('should always render a label', () => {
    renderTag({ label: 'Département' })

    expect(screen.getByText('Département')).toBeInTheDocument()
  })

  it('should render an icon if provided', () => {
    const { container } = renderTag({ label: 'Département', icon: 'icon.svg' })

    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('should not render an icon if not provided', () => {
    const { container } = renderTag({ label: 'Département' })

    expect(container.querySelector('svg')).not.toBeInTheDocument()
  })

  it('should not render an icon for new variant', () => {
    const { container } = renderTag({
      label: 'Département',
      icon: 'icon.svg',
      variant: TagVariant.NEW,
    })
    expect(container.querySelector('svg')).not.toBeInTheDocument()
  })

  it.each([TagVariant.BOOKCLUB, TagVariant.HEADLINE, TagVariant.LIKE])(
    'should always render an icon for specific variant: %s',
    (variant) => {
      const { container } = renderTag({
        label: 'Département',
        variant: variant,
      })

      expect(container.querySelector('svg')).toBeInTheDocument()
    }
  )
})
