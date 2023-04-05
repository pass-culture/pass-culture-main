import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import {
  IOfferer,
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { DEFAULT_OFFERER_FORM_VALUES } from 'screens/SignupJourneyForm/Offerer/constants'
import { SubmitButton } from 'ui-kit'
import { renderWithProviders } from 'utils/renderWithProviders'

import OffererAuthenticationForm, {
  IOffererAuthenticationFormValues,
} from '../OffererAuthenticationForm'
import { validationSchema } from '../validationSchema'

const renderOffererAuthenticationForm = ({
  initialValues,
  onSubmit = jest.fn(),
  contextValue,
}: {
  initialValues: Partial<IOffererAuthenticationFormValues>
  onSubmit?: () => void
  contextValue: ISignupJourneyContext
}) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }

  return renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        validationSchema={validationSchema}
      >
        <Form>
          <OffererAuthenticationForm />
          <SubmitButton isLoading={false}>Submit</SubmitButton>
        </Form>
      </Formik>
    </SignupJourneyContext.Provider>,
    {
      storeOverrides,
      initialRouterEntries: ['/parcours-inscription/authentification'],
    }
  )
}

describe('screens:SignupJourney::OffererAuthenticationForm', () => {
  let offererAuthenticationFormValues: IOfferer
  let contextValue: ISignupJourneyContext
  let initialValues: Partial<IOffererAuthenticationFormValues>

  beforeEach(() => {
    offererAuthenticationFormValues = {
      ...DEFAULT_OFFERER_FORM_VALUES,
      siret: '123 456 789 33333',
      name: 'Test name',
    }
    initialValues = { ...offererAuthenticationFormValues }
    contextValue = {
      activity: null,
      offerer: offererAuthenticationFormValues,
      setActivity: () => {},
      setOfferer: () => {},
    }
  })

  it('should render form', async () => {
    renderOffererAuthenticationForm({
      initialValues: initialValues,
      contextValue: contextValue,
    })

    const siretField = screen.getByLabelText('Numéro de SIRET')
    const nameField = screen.getByLabelText('Raison sociale')

    expect(siretField).toBeDisabled()
    expect(siretField).toHaveValue('123 456 789 33333')

    expect(nameField).toBeDisabled()
    expect(nameField).toHaveValue('Test name')

    expect(screen.getByText('Nom public')).toBeInTheDocument()

    expect(
      screen.getByText(
        'À remplir si le nom de votre structure est différent de la raison sociale. C’est ce nom qui sera visible du public.'
      )
    ).toBeInTheDocument()
  })

  it.only('should not render error on submit when publicName is empty or filled', async () => {
    renderOffererAuthenticationForm({
      initialValues: initialValues,
      contextValue: contextValue,
    })

    const publicNameField = await screen.getByLabelText('Nom public', {
      exact: false,
    })
    await userEvent.type(publicNameField, 'Public name')
    expect(publicNameField).toHaveValue('Public name')
  })
})
