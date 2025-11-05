import { render, screen } from '@testing-library/react'

import { HighlightDatespanTag } from './HighlightDatespanTag'

describe('HighlightDatespanTag', () => {
  it('should display two date when they are different', () => {
    render(
      <HighlightDatespanTag
        highlightDatespan={[
          '2025-11-14T09:58:22.640Z',
          '2025-11-15T09:58:22.640Z',
        ]}
      />
    )

    expect(screen.getByText('14/11/2025')).toBeInTheDocument()
    expect(screen.getByText('au')).toBeInTheDocument()
    expect(screen.getByText('15/11/2025')).toBeInTheDocument()
  })

  it('should display one date when they are the same', () => {
    render(
      <HighlightDatespanTag
        highlightDatespan={[
          '2025-11-15T09:58:22.640Z',
          '2025-11-15T09:58:22.640Z',
        ]}
      />
    )

    expect(screen.getByText('15/11/2025')).toBeInTheDocument()
    expect(screen.queryByText('au')).not.toBeInTheDocument()
  })
})
