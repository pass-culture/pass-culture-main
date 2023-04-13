import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import fetch from 'jest-fetch-mock'
import React from 'react'

import { apiAdresse } from 'apiClient/adresse'
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

jest.mock('apiClient/adresse', () => {
  return {
    ...jest.requireActual('apiClient/adresse'),
    default: {
      getDataFromAddress: jest.fn(),
    },
  }
})

jest.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue([
  {
    address: '12 rue des lilas',
    city: 'Lyon',
    id: '1',
    latitude: 11.1,
    longitude: -11.1,
    label: '12 rue des lilas 69002 Lyon',
    postalCode: '69002',
  },
  {
    address: '12 rue des tournesols',
    city: 'Paris',
    id: '2',
    latitude: 22.2,
    longitude: -2.22,
    label: '12 rue des tournesols 75003 Paris',
    postalCode: '75003',
  },
])

fetch.mockResponse(
  JSON.stringify({
    features: [
      {
        properties: {
          name: 'name',
          city: 'city',
          id: 'id',
          label: 'label',
          postcode: 'postcode',
        },
        geometry: {
          coordinates: [0, 0],
        },
      },
    ],
  }),
  { status: 200 }
)

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
