import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'

import { Mode } from 'core/OfferEducational'
import { RootState } from 'store/reducers'

import { defaultEditionProps, renderEACOfferForm } from '../__tests-utils__'
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
  NOTIFICATIONS_LABEL,
  OFFERER_LABEL,
  PHONE_LABEL,
  SUBCATEGORY_LABEL,
  TITLE_LABEL,
  VENUE_LABEL,
} from '../constants/labels'
import { IOfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational', () => {
  let props: IOfferEducationalProps
  let store: Partial<RootState>

  beforeEach(() => {
    props = defaultEditionProps
    store = {
      features: {
        initialized: true,
        list: [],
      },
    }
  })

  it('should disable all fiels when mode is READONLY', async () => {
    props.userOfferers = [
      ...props.userOfferers,
      userOffererFactory({
        id: 'OFFERER_WITH_INTERVENTION_AREA',
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
      mode: Mode.READ_ONLY,
    }
    renderEACOfferForm(props, store)

    const inputs = await Promise.all([
      screen.findByLabelText(CATEGORY_LABEL),
      screen.findByLabelText(SUBCATEGORY_LABEL),
      screen.findByLabelText(TITLE_LABEL),
      screen.findByLabelText(CATEGORY_LABEL),
      screen.findByLabelText(DURATION_LABEL, { exact: false }),
      screen.findByLabelText(OFFERER_LABEL),
      screen.findByLabelText(VENUE_LABEL),
      screen.findByLabelText('Autre'), // one of every option
      screen.findByLabelText('Collège - 3e'), // one of every option
      screen.findByLabelText('Visuel'), // one of every option
      screen.findByLabelText(PHONE_LABEL),
      screen.findByLabelText(EMAIL_LABEL),
      screen.findByLabelText(NOTIFICATIONS_LABEL),
      screen.findByLabelText(NOTIFICATIONS_EMAIL_LABEL),
      screen.findByLabelText(INTERVENTION_AREA_LABEL),
    ])
    const submitButton = await screen.findByRole('button', {
      name: 'Enregistrer',
    })

    inputs.forEach(input => expect(input).toBeDisabled())
    expect(submitButton).toBeDisabled()
  })
})
