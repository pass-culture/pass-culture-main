import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { expect } from 'vitest'

import { api } from '@/apiClient//api'
import { VenueTypeResponseModel } from '@/apiClient//v1'
import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import {
  ActivityContext,
  SignupJourneyContext,
  SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { defaultActivityFormValues } from '@/components/SignupJourneyForm/Activity/constants'
import { Button } from '@/ui-kit/Button/Button'

import {
  ActivityForm,
  ActivityFormProps,
  ActivityFormValues,
} from '../ActivityForm'

vi.mock('@/apiClient//api', () => ({
  api: {
    getVenueTypes: vi.fn(),
  },
}))

const venueTypes: VenueTypeResponseModel[] = [
  { id: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { id: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const onSubmit = vi.fn()

function renderActivityForm(
  initialValues: Partial<ActivityFormValues>,
  props: ActivityFormProps,
  contextValue: SignupJourneyContextValues
) {
  const Wrapper = () => {
    const methods = useForm({
      defaultValues: initialValues,
    })
    return (
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <ActivityForm {...props} />
          <Button type="submit" isLoading={false}>
            Étape suivante
          </Button>
        </form>
      </FormProvider>
    )
  }

  renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <Wrapper />
    </SignupJourneyContext.Provider>
  )
}

describe('screens:SignupJourney::ActivityForm', () => {
  let activity: ActivityContext
  let contextValue: SignupJourneyContextValues
  let props: ActivityFormProps
  let initialValues: Partial<ActivityFormValues>
  beforeEach(() => {
    activity = DEFAULT_ACTIVITY_VALUES
    initialValues = defaultActivityFormValues
    props = {
      venueTypes: venueTypes,
    }
    contextValue = {
      activity: activity,
      offerer: null,
      setActivity: () => {},
      setOfferer: () => {},
    }
    vi.spyOn(api, 'getVenueTypes').mockResolvedValue([])
  })

  it('should render activity form', async () => {
    renderActivityForm(initialValues, props, contextValue)

    expect(screen.getByLabelText('Activité principale *')).toHaveValue('')
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(1)
    expect(
      await screen.findByRole('button', { name: 'Ajouter un lien' })
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText('Au grand public', {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText('À des groupes scolaires', {
        exact: false,
      })
    ).not.toBeChecked()
  })

  it('should render activity form with initialValues', () => {
    initialValues = {
      venueTypeCode: 'MUSEUM',
      socialUrls: [
        { url: 'https://example.com' },
        { url: 'https://exampleTwo.fr' },
      ],
      targetCustomer: { individual: false, educational: false },
    }

    renderActivityForm(initialValues, props, contextValue)

    expect(
      screen.getByText('Cours et pratique artistiques')
    ).toBeInTheDocument()
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(2)
    expect(
      screen.getByLabelText('Au grand public', {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText('À des groupes scolaires', {
        exact: false,
      })
    ).not.toBeChecked()
  })

  it('should not navigate to the next step if activity form is not valid', async () => {
    renderActivityForm(initialValues, props, contextValue)

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.queryByText('Validation screen')).not.toBeInTheDocument()
  })

  it('should add social url input on click add url button', async () => {
    renderActivityForm(initialValues, props, contextValue)

    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(1)
    await userEvent.click(screen.getByText('Ajouter un lien'))
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(2)
  })

  it('should remove social url input on click remove url button', async () => {
    initialValues.socialUrls = [
      { url: 'https://example.com' },
      { url: 'https://exampleTwo.fr' },
    ]
    renderActivityForm(initialValues, props, contextValue)

    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(2)

    const trashButtons = screen.getAllByRole('button', {
      name: 'Supprimer l’url',
    })

    await userEvent.click(trashButtons[0])
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(1)
    expect(screen.queryByText('https://example.fr')).not.toBeInTheDocument()
    expect(
      screen.getByDisplayValue('https://exampleTwo.fr')
    ).toBeInTheDocument()
  })

  it('should change targetCustomer value on click', async () => {
    renderActivityForm(initialValues, props, contextValue)

    const publicTarget = screen.getByLabelText('Au grand public')
    const schoolTarget = screen.getByLabelText('À des groupes scolaires')

    expect(publicTarget).not.toBeChecked()
    expect(schoolTarget).not.toBeChecked()

    await userEvent.click(publicTarget)
    expect(publicTarget).toBeChecked()

    await userEvent.click(schoolTarget)
    expect(schoolTarget).toBeChecked()
    expect(publicTarget).toBeChecked()

    await userEvent.click(publicTarget)
    expect(schoolTarget).toBeChecked()
    expect(publicTarget).not.toBeChecked()
  })

  it('should change venueType', async () => {
    renderActivityForm(initialValues, props, contextValue)

    const venueTypeSelect = screen.getByLabelText('Activité principale *')
    expect(venueTypeSelect).toHaveValue('')

    await userEvent.click(venueTypeSelect)
    await userEvent.click(screen.getByText('Culture scientifique'))
    await waitFor(() => {
      expect(screen.getByText('Culture scientifique')).toBeInTheDocument()
    })
  })
})
