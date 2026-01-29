import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { TipsBanner } from './TipsBanner'

describe('TipsBanner', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<TipsBanner>Ceci est un tip.</TipsBanner>)

    expect(container).toBeInTheDocument()
    expect(screen.getByText('À savoir')).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render provided text', () => {
    const longText = `Vous pouvez modifier la mise en forme de votre texte. Utilisez des doubles astérisques pour mettre en gras : **exemple** et des tirets bas pour l’italique : _exemple_. Vous pourrez vérifier l’affichage à l’étape "Aperçu".`
    render(<TipsBanner>{longText}</TipsBanner>)

    expect(screen.getByText(longText)).toBeInTheDocument()
  })

  it('should render provided illustration', () => {
    const illustrationSrc = 'https://example.com/illustration.png'
    render(
      <TipsBanner decorativeImage={illustrationSrc}>
        Ceci est un tip avec une illustration.
      </TipsBanner>
    )

    const imgElement = screen.getByRole('presentation')
    expect(imgElement).toBeInTheDocument()
    expect(imgElement).toHaveAttribute('src', illustrationSrc)
  })
})
