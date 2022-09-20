import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { PARTICIPANTS } from 'core/OfferEducational'

import FormParticipants from '../FormParticipants'

const initialValues = {
  participants: {
    quatrieme: true,
    troisieme: true,
    seconde: true,
    premiere: true,
    terminale: true,
    CAPAnnee1: true,
    CAPAnnee2: false,
    all: false,
  },
}

describe('FormParticipants', () => {
  it('should render all options with default value', async () => {
    render(
      <Formik initialValues={initialValues} onSubmit={() => {}}>
        <FormParticipants disableForm={false} />
      </Formik>
    )
    expect(await screen.findAllByRole('checkbox')).toHaveLength(8)
    expect(
      screen.getByRole('checkbox', { name: PARTICIPANTS.premiere })
    ).toBeChecked()
  })

  it('should trigger useParticipantHook and check "all"', async () => {
    render(
      <Formik initialValues={initialValues} onSubmit={() => {}}>
        <FormParticipants disableForm={false} />
      </Formik>
    )
    const cap2Checkbox = screen.getByRole('checkbox', {
      name: PARTICIPANTS.CAPAnnee2,
    })
    await userEvent.click(cap2Checkbox)
    await waitFor(() =>
      expect(screen.getByLabelText('Tout sélectionner')).toBeChecked()
    )
  })
})
