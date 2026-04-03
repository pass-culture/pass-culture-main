import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { EditoCardItem } from './EditoCardItem'

const defaultProps = {
  image: '/path/to/image.png',
  title: 'My title',
  subtitle: 'My subtitle',
  footer: <button>My button</button>,
}

describe('EditoCardItem', () => {
  it('should render correctly', () => {
    const { container } = renderWithProviders(
      <EditoCardItem {...defaultProps} />
    )
    expect(
      screen.getByRole('heading', { level: 3, name: 'My title' })
    ).toBeInTheDocument()
    expect(screen.getByText('My subtitle')).toBeInTheDocument()
    expect(container.querySelector('img')).toHaveAttribute(
      'src',
      '/path/to/image.png'
    )
    expect(
      screen.getByRole('button', { name: 'My button' })
    ).toBeInTheDocument()
  })
})
