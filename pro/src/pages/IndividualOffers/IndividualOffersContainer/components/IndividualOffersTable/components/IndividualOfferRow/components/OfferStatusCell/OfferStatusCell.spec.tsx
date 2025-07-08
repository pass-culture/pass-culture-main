import { screen } from '@testing-library/react'
import { addDays, format, subDays } from 'date-fns'

import { OfferStatus } from 'apiClient/v1'
import { FORMAT_DD_MM_YYYY } from 'commons/utils/date'
import { listOffersOfferFactory } from 'commons/utils/factories/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { OfferStatusCell, OfferStatusCellProps } from './OfferStatusCell'

function renderOfferStatusCell(
  props: OfferStatusCellProps,
  options?: RenderWithProvidersOptions
) {
  renderWithProviders(
    <table>
      <tbody>
        <tr>
          <OfferStatusCell {...props} />
        </tr>
      </tbody>
    </table>,
    options
  )
}

const defaultProps: OfferStatusCellProps = {
  offer: listOffersOfferFactory(),
  rowId: '',
}

const dayInTheFuture = addDays(new Date(), 2).toISOString()
const dayInThePast = subDays(new Date(), 2).toISOString()

describe('OfferStatusCell', () => {
  it('should show the date of publication if the FF WIP_REFACTO_FUTURE_OFFER is enabled', () => {
    renderOfferStatusCell(
      {
        ...defaultProps,
        offer: listOffersOfferFactory({
          publicationDatetime: dayInTheFuture,
          status: OfferStatus.SCHEDULED,
        }),
      },
      { features: ['WIP_REFACTO_FUTURE_OFFER'] }
    )

    expect(
      screen.getByText(new RegExp(format(dayInTheFuture, FORMAT_DD_MM_YYYY)))
    ).toBeInTheDocument()
  })

  it('should show the status if the FF WIP_REFACTO_FUTURE_OFFER is disabled', () => {
    renderOfferStatusCell({
      ...defaultProps,
      offer: listOffersOfferFactory({
        publicationDatetime: dayInTheFuture,
        status: OfferStatus.SCHEDULED,
      }),
    })

    expect(screen.getByText('programmée')).toBeInTheDocument()
  })

  it('should show the status if the FF WIP_REFACTO_FUTURE_OFFER is enabled and the status is published', () => {
    renderOfferStatusCell(
      {
        ...defaultProps,
        offer: listOffersOfferFactory({
          publicationDatetime: dayInTheFuture,
          status: OfferStatus.PUBLISHED,
        }),
      },
      { features: ['WIP_REFACTO_FUTURE_OFFER'] }
    )

    expect(screen.getByText('publiée')).toBeInTheDocument()
  })

  it('should show the status if the FF WIP_REFACTO_FUTURE_OFFER is enabled and the offer was published in the past', () => {
    renderOfferStatusCell(
      {
        ...defaultProps,
        offer: listOffersOfferFactory({
          publicationDatetime: dayInThePast,
          status: OfferStatus.PUBLISHED,
        }),
      },
      { features: ['WIP_REFACTO_FUTURE_OFFER'] }
    )

    expect(screen.getByText('publiée')).toBeInTheDocument()
  })
})
