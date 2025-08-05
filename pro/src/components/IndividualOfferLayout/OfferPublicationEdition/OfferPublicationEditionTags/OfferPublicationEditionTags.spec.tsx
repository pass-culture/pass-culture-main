import { OfferStatus } from 'apiClient/v1'
import { render, screen } from '@testing-library/react'
import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'
import { addDays } from 'date-fns'

import {
  OfferPublicationEditionProps,
  OfferPublicationEditionTags,
} from './OfferPublicationEditionTags'

function renderOfferPublicationEditionTags(
  props: OfferPublicationEditionProps
) {
  render(<OfferPublicationEditionTags {...props} />)
}

describe('OfferPublicationEditionTags', () => {
  it('should render the "en pause" tag if the offer is inactive', () => {
    renderOfferPublicationEditionTags({
      offer: getIndividualOfferFactory({
        status: OfferStatus.INACTIVE,
      }),
    })

    expect(screen.getByText('en pause')).toBeInTheDocument()
  })

  it('should render the "publiée" tag if the offer is active', () => {
    renderOfferPublicationEditionTags({
      offer: getIndividualOfferFactory({
        status: OfferStatus.ACTIVE,
      }),
    })

    expect(screen.getByText('publiée')).toBeInTheDocument()
  })

  it('should render the "publiée" tag if the offer is published', () => {
    renderOfferPublicationEditionTags({
      offer: getIndividualOfferFactory({
        status: OfferStatus.PUBLISHED,
      }),
    })

    expect(screen.getByText('publiée')).toBeInTheDocument()
  })

  it('should render the publication date tag if the offer is scheduled', () => {
    renderOfferPublicationEditionTags({
      offer: getIndividualOfferFactory({
        status: OfferStatus.SCHEDULED,
        publicationDatetime: addDays(new Date(), 1).toISOString(),
      }),
    })

    expect(screen.getByText(/Publication :/)).toBeInTheDocument()
  })

  it('should render the booking allowed date tag if the offer is published with a booking allowed date', () => {
    renderOfferPublicationEditionTags({
      offer: getIndividualOfferFactory({
        status: OfferStatus.PUBLISHED,
        bookingAllowedDatetime: addDays(new Date(), 1).toISOString(),
      }),
    })

    expect(screen.getByText(/Réservabilité :/)).toBeInTheDocument()
  })
})
