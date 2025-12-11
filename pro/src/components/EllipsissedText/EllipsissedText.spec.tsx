import { render, screen } from '@testing-library/react'

import { EllipsissedText } from './EllipsissedText'

describe('EllipsissedText', () => {
  it('should render children text content', () => {
    render(<EllipsissedText>Some text content</EllipsissedText>)

    expect(screen.getByText('Some text content')).toBeInTheDocument()
  })

  it('should apply ellipsissed-text class', () => {
    render(<EllipsissedText>Text</EllipsissedText>)

    const element = screen.getByText('Text')
    expect(element.className).toContain('ellipsissed-text')
  })

  it('should merge custom className with default class', () => {
    render(<EllipsissedText className="custom-class">Text</EllipsissedText>)

    const element = screen.getByText('Text')
    expect(element.className).toContain('ellipsissed-text')
    expect(element.className).toContain('custom-class')
  })

  it('should pass through additional HTML props', () => {
    render(<EllipsissedText data-testid="ellipsissed">Text</EllipsissedText>)

    expect(screen.getByTestId('ellipsissed')).toBeInTheDocument()
  })

  it('should render as a span element', () => {
    render(<EllipsissedText>Text</EllipsissedText>)

    const element = screen.getByText('Text')
    expect(element.tagName).toBe('SPAN')
  })
})
