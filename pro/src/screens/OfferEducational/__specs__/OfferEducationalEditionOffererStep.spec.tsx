import { screen } from '@testing-library/react'
import React from 'react'

import { CollectiveBookingStatus } from 'apiClient/v1'
import { Mode } from 'core/OfferEducational'
import {
  collectiveOfferFactory,
  collectiveOfferOffererFactory,
  collectiveOfferVenueFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  defaultEditionProps,
  managedVenuesFactory,
  userOfferersFactory,
} from '../__tests-utils__'
import OfferEducational, { OfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational : edition offerer step', () => {
  let props: OfferEducationalProps
  const firstvenueId = 34
  const secondVenueId = 56
  const thirdVenueId = 67
  const fourthVenueId = 92
  const firstOffererId = 45
  const secondOffererId = 92

  beforeEach(() => {
    props = defaultEditionProps
  })

  it('should display offerer and venue selects as disabled (not editable) fields', async () => {
    props = {
      ...props,
      userOfferers: userOfferersFactory([
        {
          nonHumanizedId: firstOffererId,
          managedVenues: managedVenuesFactory([
            { id: firstvenueId.toString(), nonHumanizedId: firstvenueId },
            { id: secondVenueId.toString(), nonHumanizedId: secondVenueId },
          ]),
        },
        {
          nonHumanizedId: secondOffererId,
          managedVenues: managedVenuesFactory([
            { id: thirdVenueId.toString(), nonHumanizedId: thirdVenueId },
            { id: fourthVenueId.toString(), nonHumanizedId: fourthVenueId },
          ]),
        },
      ]),
      offer: collectiveOfferFactory(
        {
          venueId: thirdVenueId.toString(),
          nonHumanizedId: thirdVenueId,
          venue: {
            ...collectiveOfferVenueFactory({
              managingOfferer: collectiveOfferOffererFactory({
                id: secondOffererId.toString(),
                nonHumanizedId: secondOffererId,
              }),
            }),
            nonHumanizedId: thirdVenueId,
            id: thirdVenueId.toString(),
          },
        },
        undefined,
        collectiveOfferVenueFactory({
          managingOffererId: secondOffererId.toString(),
        })
      ),
    }

    renderWithProviders(<OfferEducational {...props} />)

    const offerTypeTitle = await screen.findByRole('heading', {
      name: 'Type d’offre',
    })
    expect(offerTypeTitle).toBeInTheDocument()

    const offererSelect = await screen.findByLabelText('Structure')

    expect(offererSelect).toBeInTheDocument()
    expect(offererSelect).toHaveValue(secondOffererId.toString())
    expect(offererSelect).toBeDisabled()

    const venueSelect = await screen.findByLabelText('Lieu')

    expect(venueSelect).toBeInTheDocument()
    expect(venueSelect).toHaveValue(thirdVenueId.toString())
    expect(venueSelect).not.toBeDisabled()
  })

  it('should display offer and venue select disabled', async () => {
    props = {
      ...props,
      userOfferers: userOfferersFactory([
        {
          nonHumanizedId: firstOffererId,
          managedVenues: managedVenuesFactory([
            { id: firstvenueId.toString(), nonHumanizedId: firstvenueId },
            { id: secondVenueId.toString(), nonHumanizedId: secondVenueId },
          ]),
        },
        {
          nonHumanizedId: secondOffererId,
          managedVenues: managedVenuesFactory([
            { id: thirdVenueId.toString(), nonHumanizedId: thirdVenueId },
            { id: fourthVenueId.toString(), nonHumanizedId: fourthVenueId },
          ]),
        },
      ]),
      offer: collectiveOfferFactory(
        {
          venueId: thirdVenueId.toString(),
          nonHumanizedId: thirdVenueId,
          venue: {
            ...collectiveOfferVenueFactory({
              managingOfferer: collectiveOfferOffererFactory({
                id: secondOffererId.toString(),
                nonHumanizedId: secondOffererId,
              }),
            }),
            nonHumanizedId: thirdVenueId,
            id: thirdVenueId.toString(),
          },
          lastBookingStatus: CollectiveBookingStatus.USED,
        },
        undefined,
        collectiveOfferVenueFactory({
          managingOffererId: secondOffererId.toString(),
        })
      ),
    }
    renderWithProviders(<OfferEducational {...props} />)

    const venueSelect = await screen.findByLabelText('Lieu')

    expect(venueSelect).toBeInTheDocument()
    expect(venueSelect).toHaveValue(thirdVenueId.toString())
    expect(venueSelect).toBeDisabled()
  })

  it('should show banner if generate from publicApi', () => {
    const offer = collectiveOfferFactory({ isPublicApi: true })

    renderWithProviders(
      <OfferEducational {...props} mode={Mode.EDITION} offer={offer} />
    )
    expect(
      screen.getByText('Offre importée automatiquement')
    ).toBeInTheDocument()
  })
})
