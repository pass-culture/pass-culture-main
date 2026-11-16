import { screen } from '@testing-library/react'

import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { truncateAtWord } from '@/commons/utils/string'

import { OfferAppPreview } from './OfferAppPreview'
import styles from './OfferAppPreview.module.scss'

describe('OfferAppPreview', () => {
  it('keeps the full credit accessible while truncating its visible version', () => {
    const credit =
      'Photographie réalisée par Arthur et conservée dans les archives du théâtre municipal'
    const offer = getIndividualOfferFactory({
      activeMediation: {
        thumbUrl: 'https://example.com/image.jpg',
        alternativeText: 'Une scène de théâtre',
        credit,
      },
    })

    renderWithProviders(<OfferAppPreview offer={offer} />)

    const image = screen.getByRole('img', { name: 'Une scène de théâtre' })
    expect(image).toHaveAccessibleDescription(`Crédit image : ${credit}`)
    expect(screen.getByText(truncateAtWord(credit, 50))).toHaveAttribute(
      'aria-hidden',
      'true'
    )
    expect(screen.getByText(credit)).toHaveClass(styles['visually-hidden'])
    expect(image.closest('figure')).toContainElement(
      screen.getByText(credit).closest('figcaption')
    )
  })
})
