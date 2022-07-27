import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'

import {
  defaultEditionProps,
  managedVenuesFactory,
  renderEACOfferForm,
  userOfferersFactory,
} from '../__tests-utils__'
import { IOfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational : edition offerer step', () => {
  let props: IOfferEducationalProps

  beforeEach(() => {
    props = defaultEditionProps
  })

  it('should display offerer and venue selects as disabled (not editable) fields', async () => {
    props = {
      ...props,
      userOfferers: userOfferersFactory([
        {
          id: 'OFFERER_1',
          managedVenues: managedVenuesFactory([
            { id: 'VENUE_1' },
            { id: 'VENUE_2' },
          ]),
        },
        {
          id: 'OFFERER_2',
          managedVenues: managedVenuesFactory([
            { id: 'VENUE_3' },
            { id: 'VENUE_4' },
          ]),
        },
      ]),
      initialValues: {
        ...props.initialValues,
        venueId: 'VENUE_3',
        offererId: 'OFFERER_2',
      },
    }
    renderEACOfferForm(props)

    const offerTypeTitle = await screen.findByRole('heading', {
      name: 'Type d’offre',
    })
    expect(offerTypeTitle).toBeInTheDocument()

    const offererSelect = await screen.findByLabelText('Structure')

    expect(offererSelect).toBeInTheDocument()
    expect(offererSelect).toHaveValue(props.initialValues.offererId)
    expect(offererSelect).toBeDisabled()

    const venueSelect = await screen.findByLabelText(
      'Lieu qui percevra le remboursement'
    )

    expect(venueSelect).toBeInTheDocument()
    expect(venueSelect).toHaveValue(props.initialValues.venueId)
    expect(venueSelect).toBeDisabled()
  })
})
