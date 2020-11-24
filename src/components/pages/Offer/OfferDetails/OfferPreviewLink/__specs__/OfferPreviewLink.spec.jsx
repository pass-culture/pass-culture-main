import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import OfferPreviewLink from '../OfferPreviewLink'

describe('src | OfferPreviewLink', () => {
  let props

  beforeEach(() => {
    props = {
      offerId: 'TEST_OFFER_ID',
      mediationId: 'TEST_MEDIATION_ID',
    }
  })

  it('should display a link', () => {
    // when
    render(<OfferPreviewLink {...props} />)

    const link = screen.getByText('Prévisualiser')

    expect(link).toHaveAttribute(
      'href',
      `http://localhost/offre/details/${props.offerId}/${props.mediationId}`
    )
    const tip = screen.getByTestId('offer-preview-link-tooltip')
    expect(tip).toHaveAttribute(
      'data-tip',
      'Ouvrir un nouvel onglet avec la prévisualisation de l’offre.'
    )
    const icon = screen.getByTestId('offer-preview-link-icon')
    expect(icon).toHaveAttribute('src', 'http://localhost/icons/ico-eye.svg')
  })
})
