import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { expect } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import * as apiAdresse from '@/apiClient/adresse/apiAdresse'
import {
  type Offerer,
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { noop } from '@/commons/utils/noop'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { DEFAULT_OFFERER_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'
import { Button } from '@/design-system/Button/Button'

import {
  OffererAuthenticationForm,
  type OffererAuthenticationFormValues,
} from '../OffererAuthenticationForm'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

vi.mock('@/apiClient/adresse/apiAdresse', async () => {
  return {
    ...(await vi.importActual('@/apiClient/adresse/apiAdresse')),
    default: {
      getDataFromAddress: vi.fn(),
    },
  }
})

vi.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue([
  {
    address: '12 rue des lilas',
    city: 'Lyon',
    id: '1',
    latitude: 11.1,
    longitude: -11.1,
    label: '12 rue des lilas 69002 Lyon',
    postalCode: '69002',
    inseeCode: '69002',
  },
  {
    address: '12 rue des tournesols',
    city: 'Paris',
    id: '2',
    latitude: 22.2,
    longitude: -2.22,
    label: '12 rue des tournesols 75003 Paris',
    postalCode: '75003',
    inseeCode: '75003',
  },
])

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

const renderOffererAuthenticationForm = ({
  initialValues,
  onSubmit = vi.fn(),
  contextValue,
}: {
  initialValues: Partial<OffererAuthenticationFormValues>
  onSubmit?: () => void
  contextValue: SignupJourneyContextValues
}) => {
  const Wrapper = () => {
    const methods = useForm({
      defaultValues: initialValues,
    })
    return (
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <OffererAuthenticationForm />
          <Button type="submit" isLoading={false}>
            Submit
          </Button>
        </form>
      </FormProvider>
    )
  }

  renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <Wrapper />
    </SignupJourneyContext.Provider>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/identification'],
    }
  )
}

describe('OffererAuthenticationForm', () => {
  let offererAuthenticationFormValues: Offerer
  let contextValue: SignupJourneyContextValues
  let initialValues: Partial<OffererAuthenticationFormValues>

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
      initialAddress: null,
      setInitialAddress: noop,
    }
  })

  it('should render form', async () => {
    renderOffererAuthenticationForm({
      initialValues: initialValues,
      contextValue: contextValue,
    })

    const siretField = screen.getByLabelText(/Numéro de SIRET/)
    const nameField = screen.getByLabelText(/Raison sociale/)
    const addressField = screen.getByLabelText(/Adresse postale/)

    await waitFor(() => {
      expect(siretField).toBeDisabled()
      expect(siretField).toHaveValue('123 456 789 33333')

      expect(nameField).toBeDisabled()
      expect(nameField).toHaveValue('Test name')

      expect(screen.getByText('Nom public')).toBeInTheDocument()

      expect(addressField).toBeInTheDocument()

      expect(addressField).not.toBeDisabled()

      expect(
        screen.getByText(
          'À remplir si le nom de votre structure est différent de la raison sociale. C’est ce nom qui sera visible du public.'
        )
      ).toBeInTheDocument()
    })
  })

  it('should render form with manual address feature', async () => {
    renderOffererAuthenticationForm({
      initialValues: initialValues,
      contextValue: contextValue,
    })

    // The toggle button "Renseignez l’adresse manuellement" should be visible
    const manualAddressToggle = screen.getByRole('button', {
      name: 'Vous ne trouvez pas votre adresse ?',
    })

    expect(manualAddressToggle).toBeInTheDocument()

    // If user toggle manual address fields
    await userEvent.click(manualAddressToggle)

    // …then he should see the different address fields
    expect(
      screen.getByRole('textbox', { name: /Adresse postale/ })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('textbox', { name: /Code postal/ })
    ).toBeInTheDocument()

    expect(screen.getByRole('textbox', { name: /Ville/ })).toBeInTheDocument()

    expect(
      screen.getByRole('textbox', { name: /Coordonnées GPS/ })
    ).toBeInTheDocument()
  })

  it('should not render error on submit when publicName is empty or filled', async () => {
    renderOffererAuthenticationForm({
      initialValues: initialValues,
      contextValue: contextValue,
    })

    const publicNameField = screen.getByLabelText('Nom public', {
      exact: false,
    })
    await userEvent.type(publicNameField, 'Public name')
    expect(publicNameField).toHaveValue('Public name')
  })

  it('should render radio buttons to toggle open to public', async () => {
    renderOffererAuthenticationForm({
      initialValues: initialValues,
      contextValue: contextValue,
    })

    const yesRadio = await screen.findByRole('radio', { name: 'Oui' })
    const noRadio = await screen.findByRole('radio', { name: 'Non' })

    expect(yesRadio).toBeInTheDocument()
    expect(noRadio).toBeInTheDocument()
  })

  it('should render form without address when not dissufible', () => {
    renderOffererAuthenticationForm({
      initialValues: initialValues,
      contextValue: {
        ...contextValue,
        offerer: {
          ...offererAuthenticationFormValues,
          isDiffusible: false,
        },
      },
    })

    const addressField = screen.queryByLabelText('Adresse postale *')
    expect(addressField).not.toBeInTheDocument()
  })

  it('should call reset on open to public change', async () => {
    renderOffererAuthenticationForm({
      initialValues: initialValues,
      contextValue: {
        ...contextValue,
        offerer: {
          ...offererAuthenticationFormValues,
          isDiffusible: false,
        },
      },
    })

    const yesRadio = await screen.findByRole('radio', { name: 'Oui' })
    const noRadio = await screen.findByRole('radio', { name: 'Non' })

    expect(noRadio).not.toBeChecked()
    await userEvent.click(yesRadio)
    await waitFor(() => {
      expect(screen.getByLabelText('Adresse postale *')).toHaveValue('')
    })
  })
})
