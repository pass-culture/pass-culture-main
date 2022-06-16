import '@testing-library/jest-dom'

import * as yup from 'yup'

import { render, screen, waitFor } from '@testing-library/react'

import CollectiveOfferVisibility from '../CollectiveOfferVisibility'
import { Formik } from 'formik'
import { MemoryRouter } from 'react-router'
import React from 'react'
import userEvent from '@testing-library/user-event'

export const renderVisibilityStep = () => {
  const validationSchema = yup.object().shape({
    visibility: yup.string(),
  })

  render(
    <MemoryRouter>
      <Formik
        initialValues={{}}
        onSubmit={jest.fn()}
        validationSchema={validationSchema}
      >
        <CollectiveOfferVisibility getInstitutions={jest.fn()} />
      </Formik>
    </MemoryRouter>
  )
}

describe('CollectiveOfferVisibility', () => {
  beforeEach(() => {})

  it('should select visibility option', async () => {
    renderVisibilityStep()
    userEvent.click(screen.getByLabelText(/Un établissement en particulier/))
    // note : replace the expect to check that the list of institutions is displayed when the feature is developed
    await waitFor(() =>
      expect(
        screen.getByLabelText(/Un établissement en particulier/)
      ).toBeChecked()
    )
  })
})
