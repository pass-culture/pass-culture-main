import { screen } from '@testing-library/react'

import { CollectiveLocationType } from '@/apiClient/v1'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  OfferLocationCell,
  type OfferLocationCellProps,
} from './OfferLocationCell'

const props = {
  offerLocation: {
    locationType: CollectiveLocationType.SCHOOL,
  },
}

const renderOfferLocationCell = (props: OfferLocationCellProps) =>
  renderWithProviders(<OfferLocationCell {...props} />)

describe('OfferLocationCell', () => {
  it("should display Dans l'établissement when locationType is SCHOOL", () => {
    renderOfferLocationCell(props)
    expect(screen.getByText("Dans l'établissement")).toBeInTheDocument()
  })

  it('should display À déterminer when locationType is TO_BE_DEFINED', () => {
    renderOfferLocationCell({
      ...props,
      offerLocation: { locationType: CollectiveLocationType.TO_BE_DEFINED },
    })
    expect(screen.getByText('À déterminer')).toBeInTheDocument()
  })

  it('should display address details when locationType is not SCHOOL or TO_BE_DEFINED', () => {
    renderOfferLocationCell({
      ...props,
      offerLocation: {
        locationType: CollectiveLocationType.ADDRESS,
        location: {
          label: 'Toto',
          street: '123 Main St',
          postalCode: '12345',
          city: 'Paris',
          id: 0,
          //id: 0,
          isVenueLocation: false,
          isManualEdition: false,
          latitude: 0,
          longitude: 0,
        },
      },
    })
    expect(
      screen.getByText('Toto - 123 Main St 12345 Paris')
    ).toBeInTheDocument()
  })
})
