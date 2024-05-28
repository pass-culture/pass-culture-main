import { render, screen } from '@testing-library/react'

import { defaultCollectiveOffer } from 'utils/adageFactories'

import {
  AdageOfferPartnerSection,
  AdageOfferPartnerSectionProps,
} from '../AdageOfferPartnerSection'

function renderAdageOfferInfoSection(
  props: AdageOfferPartnerSectionProps = {
    offer: defaultCollectiveOffer,
  }
) {
  return render(<AdageOfferPartnerSection {...props} />)
}

describe('AdageOfferPartnerSection', () => {
  it('should show the e-mail address', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveOffer,
        contactEmail: 'test@test.co',
      },
    })

    expect(screen.getByText('test@test.co')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'E-mail' })).toBeInTheDocument()
  })

  it('should show the phone number if it is available', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveOffer,
        contactPhone: '1234554321',
      },
    })

    expect(screen.getByText('1234554321')).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Téléphone' })
    ).toBeInTheDocument()
  })

  it('should not show the phone number if it is not available', () => {
    renderAdageOfferInfoSection({
      offer: {
        ...defaultCollectiveOffer,
        contactPhone: undefined,
      },
    })

    expect(
      screen.queryByRole('heading', { name: 'Téléphone' })
    ).not.toBeInTheDocument()
  })
})
