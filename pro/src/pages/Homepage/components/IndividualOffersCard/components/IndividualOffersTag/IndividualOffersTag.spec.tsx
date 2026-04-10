import { render, screen } from '@testing-library/react'
import { addDays } from 'date-fns'
import { formatInTimeZone } from 'date-fns-tz'
import { axe } from 'vitest-axe'

import { type OfferHomeResponseModel, OfferStatus } from '@/apiClient/v1'
import { defaultOfferHomeResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { getDepartmentTimezone } from '@/commons/utils/timezone'

import { IndividualOffersTag } from './IndividualOffersTag'

describe('<IndividualOffersTag />', () => {
  it('should render without accessibility violations', async () => {
    const offer = defaultOfferHomeResponseModel
    const { container } = render(
      <IndividualOffersTag offer={offer} venueDepartement={'75'} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the number of reservations for non schedule offers', () => {
    const offer = defaultOfferHomeResponseModel
    render(<IndividualOffersTag offer={offer} venueDepartement={'75'} />)

    expect(screen.getByText('12 réservations')).toBeVisible()
  })

  it('should singularize the label when there is 1 reservation', () => {
    const offer = {
      ...defaultOfferHomeResponseModel,
      bookingsCount: 1,
    }
    render(<IndividualOffersTag offer={offer} venueDepartement={'75'} />)

    expect(screen.getByText('1 réservation')).toBeVisible()
  })

  it('should singularize the label when there is 0 reservation', () => {
    const offer = {
      ...defaultOfferHomeResponseModel,
      bookingsCount: 0,
    }
    render(<IndividualOffersTag offer={offer} venueDepartement={'75'} />)

    expect(screen.getByText('0 réservation')).toBeVisible()
  })

  it('should show the publication date on SCHEDULED offers in the offer timezone', () => {
    const tomorrow = addDays(new Date(), 1)
    const offer: OfferHomeResponseModel = {
      ...defaultOfferHomeResponseModel,
      status: OfferStatus.SCHEDULED,
      publicationDatetime: tomorrow.toISOString(),
      departmentCode: '973',
    }
    render(<IndividualOffersTag offer={offer} venueDepartement={'75'} />)

    const expectedDateText = formatInTimeZone(
      tomorrow,
      getDepartmentTimezone(offer.departmentCode),
      'dd/MM/yyyy HH:mm'
    )
    expect(screen.getByText(`Publication : ${expectedDateText}`)).toBeVisible()
  })

  it("should show the publication date on SCHEDULED offers in the venue timezone when offer doesn't have one", () => {
    const tomorrow = addDays(new Date(), 1)
    const offer: OfferHomeResponseModel = {
      ...defaultOfferHomeResponseModel,
      status: OfferStatus.SCHEDULED,
      publicationDatetime: tomorrow.toISOString(),
      departmentCode: null,
    }
    render(<IndividualOffersTag offer={offer} venueDepartement={'974'} />)

    const expectedDateText = formatInTimeZone(
      tomorrow,
      getDepartmentTimezone('974'),
      'dd/MM/yyyy HH:mm'
    )
    expect(screen.getByText(`Publication : ${expectedDateText}`)).toBeVisible()
  })
})
