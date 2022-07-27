import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'

import { Mode } from 'core/OfferEducational'

import { defaultEditionProps, renderEACOfferForm } from '../__tests-utils__'
import {
  CATEGORY_LABEL,
  DURATION_LABEL,
  EMAIL_LABEL,
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

  beforeEach(() => {
    props = defaultEditionProps
  })

  it('should disable all fiels when mode is READONLY', async () => {
    props = {
      ...props,
      mode: Mode.READ_ONLY,
    }
    renderEACOfferForm(props)

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
    ])
    const submitButton = await screen.findByRole('button', {
      name: 'Enregistrer',
    })

    inputs.forEach(input => expect(input).toBeDisabled())
    expect(submitButton).toBeDisabled()
  })
})
