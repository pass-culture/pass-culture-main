import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import createFetchMock from 'vitest-fetch-mock'

import { api } from 'apiClient/api'
import {
  SignupJourneyContextValues,
  SignupJourneyContext,
  Offerer,
} from 'context/SignupJourneyContext/SignupJourneyContext'
import { Button } from 'ui-kit/Button/Button'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { DEFAULT_OFFERER_FORM_VALUES } from '../constants'
import { OffererForm, OffererFormValues } from '../OffererForm'
import { validationSchema } from '../validationSchema'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

vi.mock('apiClient/api', () => ({
  api: {
    getSiretInfo: vi.fn(),
  },
}))

// Mock l’appel à https://api-adresse.data.gouv.fr/search/?limit=${limit}&q=${address}
// Appel fait dans apiAdresse.getDataFromAddress
fetchMock.mockResponse(
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
  onSubmit = vi.fn(),
  contextValue,
}: {
  initialValues: Partial<OffererFormValues>
  onSubmit?: () => void
  contextValue: SignupJourneyContextValues
}) => {
  return renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        validationSchema={validationSchema}
      >
        <Form>
          <OffererForm setShowInvisibleBanner={vi.fn()} />
          <Button type="submit" isLoading={false}>
            Submit
          </Button>
        </Form>
      </Formik>
    </SignupJourneyContext.Provider>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/parcours-inscription/siret'],
    }
  )
}

describe('screens:SignupJourney::OffererForm', () => {
  let offerer: Offerer
  let contextValue: SignupJourneyContextValues
  let initialValues: Partial<OffererFormValues>
  beforeEach(() => {
    offerer = DEFAULT_OFFERER_FORM_VALUES
    initialValues = { ...offerer }
    contextValue = {
      activity: null,
      offerer: offerer,
      setActivity: () => {},
      setOfferer: () => {},
    }
    vi.spyOn(api, 'getSiretInfo').mockResolvedValue({
      active: true,
      address: {
        city: 'Paris',
        postalCode: '75008',
        street: 'rue du test',
      },
      name: 'Test',
      siret: '12345678933333',
      ape_code: '95.01A',
      legal_category_code: '1000',
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
      screen.getByText('Tous les champs suivis d’un * sont obligatoires.')
    ).toBeInTheDocument()

    expect(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *')
    ).toHaveValue('')
  })

  it('should render offerer form with initialValues', () => {
    initialValues = {
      siret: '123456789333',
    }
    renderOffererForm({
      initialValues: initialValues,
      contextValue,
    })
    expect(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *')
    ).toHaveValue('123456789333')
  })

  it('should fill siret field only with numbers', async () => {
    renderOffererForm({
      initialValues: initialValues,
      contextValue,
    })

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      'AbdqsI'
    )

    expect(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *')
    ).toHaveValue('')
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
  it.each(lenErrorCondition)('should render errors', async (siretValue) => {
    renderOffererForm({
      initialValues: initialValues,
      contextValue,
    })

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      siretValue
    )
    await userEvent.click(screen.getByText('Submit'))
    expect(
      await screen.findByText('Le SIRET doit comporter 14 caractères')
    ).toBeInTheDocument()
  })
})
