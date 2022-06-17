import '@testing-library/jest-dom'
import 'react-router-dom'

import * as yup from 'yup'

import { render, screen, waitFor } from '@testing-library/react'

import CollectiveOfferVisibility from '../CollectiveOfferVisibility'
import { Formik } from 'formik'
import { MemoryRouter } from 'react-router'
import { Mode } from 'core/OfferEducational'
import { Provider } from 'react-redux'
import React from 'react'
import { configureTestStore } from 'store/testUtils'
import userEvent from '@testing-library/user-event'

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offerId: 'BQ',
  }),
}))

export const renderVisibilityStep = () => {
  const validationSchema = yup.object().shape({
    visibility: yup.string(),
  })

  render(
    <Provider store={configureTestStore()}>
      <MemoryRouter>
        <Formik
          initialValues={{}}
          onSubmit={jest.fn()}
          validationSchema={validationSchema}
        >
          <CollectiveOfferVisibility
            getInstitutions={jest.fn()}
            mode={Mode.CREATION}
            patchInstitution={jest.fn()}
          />
        </Formik>
      </MemoryRouter>
    </Provider>
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
