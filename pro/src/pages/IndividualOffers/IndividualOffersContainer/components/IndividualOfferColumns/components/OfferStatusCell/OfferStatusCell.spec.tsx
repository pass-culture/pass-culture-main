import { screen } from '@testing-library/react'
import { addDays, format, subDays } from 'date-fns'

import { OfferStatus } from '@/apiClient/v1'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import { listOffersOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { OfferStatusCell, type OfferStatusCellProps } from './OfferStatusCell'

function renderOfferStatusCell(
  props: OfferStatusCellProps,
  options?: RenderWithProvidersOptions
) {
  renderWithProviders(<OfferStatusCell {...props} />, options)
}

const defaultProps: OfferStatusCellProps = {
  offer: listOffersOfferFactory(),
}

describe('OfferStatusCell', () => {
  let dayInTheFuture: string
  let dayInThePast: string

  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-09-01T12:00:00.000Z'))

    dayInTheFuture = addDays(new Date(), 2).toISOString()
    dayInThePast = subDays(new Date(), 2).toISOString()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

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
