import { screen } from '@testing-library/react'

import {
  defaultGetOffererResponseModel,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OfferTypeScreen, type OfferTypeScreenProps } from './OfferType'

const defaultProps: OfferTypeScreenProps = { collectiveOnly: false }

const renderOfferTypeScreen = (props: Partial<OfferTypeScreenProps>) => {
  renderWithProviders(<OfferTypeScreen {...defaultProps} {...props} />, {
    storeOverrides: {
      offerer: {
        currentOfferer: { ...defaultGetOffererResponseModel, id: 1 },
        offererNames: [],
      },
      user: {
        selectedVenue: makeVenueListItem({ id: 2 }),
      },
    },
  })
}

describe('OfferType', () => {
  it('should show the individual option if the form is collective only', () => {
    renderOfferTypeScreen({})

    expect(
      screen.getByRole('heading', { name: 'À qui destinez-vous cette offre ?' })
    ).toBeInTheDocument()
  })

  it('should not show the individual option if the query params contain the type "collective"', () => {
    renderOfferTypeScreen({ collectiveOnly: true })

    expect(
      screen.queryByRole('heading', {
        name: 'À qui destinez-vous cette offre ?',
      })
    ).not.toBeInTheDocument()
  })
})
