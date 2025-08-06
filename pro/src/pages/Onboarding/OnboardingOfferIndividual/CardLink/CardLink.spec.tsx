import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { CardLink, type CardLinkProps } from './CardLink'

const renderCardLink = (
  props: CardLinkProps,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<CardLink {...props} />, { ...options })
}

describe('<CardLink />', () => {
  it('should render correctly with no a11y violations', async () => {
    const { container } = renderCardLink({ to: '/', label: 'Un bien physique' })

    expect(
      await screen.findByRole('link', { name: 'Un bien physique' })
    ).toBeInTheDocument()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render in horizontal mode by default', () => {
    renderCardLink({ to: '/', label: 'Un bien physique' })

    const cardLink = screen.getByRole('link', { name: 'Un bien physique' })

    expect(cardLink.closest('.cardlink')).not.toHaveClass('cardlink-vertical')
  })

  it('should render in vertical mode when specified', () => {
    renderCardLink({
      to: '/',
      label: 'Un bien physique',
      direction: 'vertical',
    })

    const cardLink = screen.getByRole('link', { name: 'Un bien physique' })

    expect(cardLink.closest('.cardlink')).toHaveClass('cardlink-vertical')
  })

  it('should render a description when specified', () => {
    const description = 'Description text'
    renderCardLink({ to: '/', label: 'Un bien physique', description })

    const descriptionElement = screen.getByText(description)

    expect(descriptionElement).toBeInTheDocument()
    expect(descriptionElement).toHaveClass('cardlink-description')
  })
})
