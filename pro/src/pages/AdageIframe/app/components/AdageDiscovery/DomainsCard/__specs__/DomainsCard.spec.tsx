import { render, screen } from '@testing-library/react'

import DomainsCard, { DomainsCardProps } from '../DomainsCard'

const renderDomainsCardComponent = ({
  title,
  color,
  src,
  href,
  handlePlaylistElementTracking,
}: DomainsCardProps) => {
  render(
    <DomainsCard
      title={title}
      color={color}
      src={src}
      href={href}
      handlePlaylistElementTracking={handlePlaylistElementTracking}
    />
  )
}

describe('CardOffer component', () => {
  it('should render domains card', () => {
    renderDomainsCardComponent({
      title: 'Test domains card',
      color: 'green',
      src: 'src',
      href: 'href',
      handlePlaylistElementTracking: vi.fn(),
    })

    expect(screen.getByText('Test domains card')).toBeInTheDocument()
  })
})
