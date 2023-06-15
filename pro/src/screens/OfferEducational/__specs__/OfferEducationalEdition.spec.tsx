import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { Mode } from 'core/OfferEducational'
import {
  collectiveOfferFactory,
  collectiveOfferVenueFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { defaultEditionProps } from '../__tests-utils__'
import {
  managedVenueFactory,
  userOffererFactory,
} from '../__tests-utils__/userOfferersFactory'
import {
  CATEGORY_LABEL,
  DURATION_LABEL,
  EMAIL_LABEL,
  INTERVENTION_AREA_LABEL,
  NOTIFICATIONS_EMAIL_LABEL,
  OFFERER_LABEL,
  SUBCATEGORY_LABEL,
  TITLE_LABEL,
  VENUE_LABEL,
} from '../constants/labels'
import OfferEducational, { IOfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational', () => {
  let props: IOfferEducationalProps

  beforeEach(() => {
    props = defaultEditionProps
  })

  it('should disable all fields when mode is READONLY', async () => {
    props.userOfferers = [
      ...props.userOfferers,
      userOffererFactory({
        managedVenues: [
          managedVenueFactory({}),
          managedVenueFactory({
            id: 'VENUE_WITH_INTERVENTION_AREA',
            collectiveInterventionArea: ['01', '02'],
          }),
        ],
      }),
    ]
    props = {
      ...props,
      offer: collectiveOfferFactory(
        { venueId: 'VENUE_WITH_INTERVENTION_AREA' },
        undefined,
        collectiveOfferVenueFactory({
          managingOffererId: 'OFFERER_WITH_INTERVENTION_AREA',
        })
      ),
      mode: Mode.READ_ONLY,
    }
    renderWithProviders(<OfferEducational {...props} />)
    await screen.findByLabelText(VENUE_LABEL)

    const inputs = [
      screen.getByLabelText(CATEGORY_LABEL),
      screen.getByLabelText(SUBCATEGORY_LABEL),
      screen.getByLabelText(TITLE_LABEL),
      screen.getByLabelText(CATEGORY_LABEL),
      screen.getByLabelText(DURATION_LABEL, { exact: false }),
      screen.getByLabelText(OFFERER_LABEL),
      screen.getByLabelText(VENUE_LABEL),
      screen.getByLabelText('Autre'), // one of every option
      screen.getByLabelText('Collège - 3e'), // one of every option
      screen.getByLabelText('Visuel'), // one of every option
      screen.getByLabelText('Téléphone', { exact: false }),
      screen.getByLabelText(EMAIL_LABEL),
      screen.getByLabelText(NOTIFICATIONS_EMAIL_LABEL),
      screen.getByLabelText(INTERVENTION_AREA_LABEL),
    ]
    const submitButton = screen.getByRole('button', {
      name: 'Enregistrer',
    })
    await waitFor(() => {
      inputs.forEach(input => expect(input).toBeDisabled())
    })
    expect(submitButton).toBeDisabled()
  })
})
