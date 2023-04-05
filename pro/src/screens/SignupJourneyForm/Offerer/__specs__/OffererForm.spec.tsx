import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import fetch from 'jest-fetch-mock'
import React from 'react'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import {
  IOfferer,
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { SubmitButton } from 'ui-kit'
import { renderWithProviders } from 'utils/renderWithProviders'

import { DEFAULT_OFFERER_FORM_VALUES } from '../constants'
import OffererForm, { IOffererFormValues } from '../OffererForm'
import { validationSchema } from '../validationSchema'

jest.mock('apiClient/api', () => ({
  api: {
    getSiretInfo: jest.fn(),
  },
}))

// Mock l'appel à https://api-adresse.data.gouv.fr/search/?limit=${limit}&q=${address}
// Appel fait dans apiAdresse.getDataFromAddress
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

const renderOffererForm = ({
  initialValues,
  onSubmit = jest.fn(),
  contextValue,
}: {
  initialValues: Partial<IOffererFormValues>
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
          <OffererForm />
          <SubmitButton isLoading={false}>Submit</SubmitButton>
        </Form>
      </Formik>
    </SignupJourneyContext.Provider>,
    { storeOverrides, initialRouterEntries: ['/parcours-inscription/siret'] }
  )
}

describe('screens:SignupJourney::OffererForm', () => {
  let offerer: IOfferer
  let contextValue: ISignupJourneyContext
  let initialValues: Partial<IOffererFormValues>
  beforeEach(() => {
    offerer = DEFAULT_OFFERER_FORM_VALUES
    initialValues = { ...offerer }
    contextValue = {
      activity: null,
      offerer: offerer,
      setActivity: () => {},
      setOfferer: () => {},
    }
    jest.spyOn(api, 'getSiretInfo').mockResolvedValue({
      active: true,
      address: {
        city: 'Paris',
        postalCode: '75008',
        street: 'rue du test',
      },
      name: 'Test',
      siret: '12345678933333',
    })
  })

  it('should render offerer form', async () => {
    renderOffererForm({
      initialValues: initialValues,
      contextValue,
    })

    expect(
      await screen.findByText('Renseignez le SIRET de votre structure')
    ).toBeInTheDocument()

    expect(
      await screen.getByText(
        'Tous les champs sont obligatoires sauf mention contraire.'
      )
    ).toBeInTheDocument()

    expect(
      await screen.getByLabelText('Numéro de SIRET à 14 chiffres')
    ).toHaveValue('')
  })

  it('should render offerer form with initialValues', async () => {
    initialValues = {
      siret: '123456789333',
    }
    renderOffererForm({
      initialValues: initialValues,
      contextValue,
    })
    expect(
      await screen.getByLabelText('Numéro de SIRET à 14 chiffres')
    ).toHaveValue('123456789333')
  })

  it('should fill siret field only with numbers', async () => {
    renderOffererForm({
      initialValues: initialValues,
      contextValue,
    })

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres'),
      'AbdqsI'
    )

    expect(screen.getByLabelText('Numéro de SIRET à 14 chiffres')).toHaveValue(
      ''
    )
  })

  it('should render empty siret field error', async () => {
    renderOffererForm({
      initialValues: initialValues,
      contextValue,
    })
    await userEvent.click(screen.getByText('Submit'))
    expect(
      await screen.findByText('Veuillez renseigner un SIRET')
    ).toBeInTheDocument()
  })

  const lenErrorCondition = ['22223333', '1234567891234567']
  it.each(lenErrorCondition)('should render errors', async siretValue => {
    renderOffererForm({
      initialValues: initialValues,
      contextValue,
    })

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres'),
      siretValue
    )
    await userEvent.click(screen.getByText('Submit'))
    expect(
      await screen.findByText('Le SIRET doit comporter 14 caractères')
    ).toBeInTheDocument()
  })

  it("should render error message when siret doesn't exist", async () => {
    jest.spyOn(api, 'getSiretInfo').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 422,
          body: [{ error: ['No SIRET'] }],
        } as ApiResult,
        ''
      )
    )

    renderOffererForm({
      initialValues: initialValues,
      contextValue,
    })

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres'),
      '12345678999999'
    )
    await userEvent.click(screen.getByText('Submit'))
    expect(await screen.findByText('Le SIRET n’existe pas')).toBeInTheDocument()
  })
})
