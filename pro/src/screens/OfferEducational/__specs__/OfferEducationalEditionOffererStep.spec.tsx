import '@testing-library/jest-dom'

import {
  defaultEditionProps,
  managedVenuesFactory,
  renderEACOfferForm,
  userOfferersFactory,
  elements,
} from '../__tests-utils__'
import { IOfferEducationalProps } from '../OfferEducational'

const { queryOffererSelect, queryVenueSelect, findOfferTypeTitle } = elements
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

    const offerTypeTitle = await findOfferTypeTitle()

    const offererSelect = queryOffererSelect()

    expect(offererSelect.input).toBeInTheDocument()
    expect(offererSelect.input?.value).toBe(props.initialValues.offererId)
    expect(offererSelect.input).toBeDisabled()

    const venueSelect = queryVenueSelect()

    expect(venueSelect.input).toBeInTheDocument()
    expect(venueSelect.input?.value).toBe(props.initialValues.venueId)
    expect(venueSelect.input).toBeDisabled()

    expect(offerTypeTitle).toBeInTheDocument()
  })
})
