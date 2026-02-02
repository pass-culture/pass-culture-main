import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import useSWR, { type SWRResponse } from 'swr'
import { expect, vi } from 'vitest'

import { DEFAULT_ACTIVITY_VALUES } from '@/commons/context/SignupJourneyContext/constants'
import {
  type ActivityContext,
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { noop } from '@/commons/utils/noop'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { defaultActivityFormValues } from '@/components/SignupJourneyForm/Activity/constants'
import { DEFAULT_OFFERER_FORM_VALUES } from '@/components/SignupJourneyForm/Offerer/constants'
import { Button } from '@/design-system/Button/Button'

import { ActivityForm, type ActivityFormValues } from '../ActivityForm'

vi.mock('swr', async (importOriginal) => ({
  ...(await importOriginal()),
  default: vi.fn(),
}))

const onSubmit = vi.fn()

function renderActivityForm(
  initialValues: Partial<ActivityFormValues>,
  contextValue: SignupJourneyContextValues
) {
  const Wrapper = () => {
    const methods = useForm({
      defaultValues: initialValues,
    })
    return (
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <ActivityForm />
          <Button type="submit" label="Étape suivante" isLoading={false} />
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
  const useSWRMock = vi.mocked(useSWR)
  let activity: ActivityContext
  let contextValue: SignupJourneyContextValues
  let initialValues: Partial<ActivityFormValues>
  beforeEach(() => {
    activity = DEFAULT_ACTIVITY_VALUES
    initialValues = defaultActivityFormValues
    contextValue = {
      activity: activity,
      offerer: { ...DEFAULT_OFFERER_FORM_VALUES, isOpenToPublic: 'true' },
      setActivity: () => {},
      setOfferer: () => {},
      initialAddress: null,
      setInitialAddress: noop,
    }
    useSWRMock.mockReturnValue({
      isLoading: false,
      data: [
        {
          id: 1,
          name: 'domaine 1',
          nationalPrograms: [],
        },
        {
          id: 2,
          name: 'domaine b',
          nationalPrograms: [],
        },
        {
          id: 3,
          name: 'domaine III',
          nationalPrograms: [],
        },
      ],
    } as SWRResponse)
  })

  it('should render activity form', async () => {
    renderActivityForm(initialValues, contextValue)

    expect(screen.getByLabelText(/Activité principale/)).toHaveValue('')
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

    // Cultural domains
    const multiSelect = screen.getByLabelText(
      'Sélectionnez un ou plusieurs domaines d’activité'
    )

    expect(multiSelect).toBeInTheDocument()
    await userEvent.click(multiSelect)
    await waitFor(() => {
      expect(screen.getByTestId('panel-scrollable')).toBeInTheDocument()
    })
    expect(screen.getByText(/3 résultats trouvés/)).toBeInTheDocument()
    expect(screen.getByText(/domaine III/)).toBeInTheDocument()
  })

  it('should render activity form with initialValues', async () => {
    initialValues = {
      activity: 'MUSEUM',
      socialUrls: [
        { url: 'https://example.com' },
        { url: 'https://exampleTwo.fr' },
      ],
      targetCustomer: { individual: false, educational: false },
      culturalDomains: ['domaine 1'],
    }

    renderActivityForm(initialValues, contextValue)

    expect(screen.getByText('Musée')).toBeInTheDocument()
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

    await userEvent.click(screen.getByLabelText('domaine sélectionné'))
    await waitFor(() => {
      expect(screen.getByTestId('panel-scrollable')).toBeInTheDocument()
    })
    expect(screen.getAllByText(/domaine 1/)).toHaveLength(2)
  })

  it('should not navigate to the next step if activity form is not valid', async () => {
    renderActivityForm(initialValues, contextValue)

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.queryByText('Validation screen')).not.toBeInTheDocument()
  })

  it('should add social url input on click add url button', async () => {
    renderActivityForm(initialValues, contextValue)

    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(1)
    await userEvent.click(screen.getByText('Ajouter un lien'))
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(2)
  })

  it('should remove social url input on click remove url button', async () => {
    initialValues.socialUrls = [
      { url: 'https://example.com' },
      { url: 'https://exampleTwo.fr' },
    ]
    renderActivityForm(initialValues, contextValue)

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
    renderActivityForm(initialValues, contextValue)

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

  it('should change activity', async () => {
    renderActivityForm(initialValues, contextValue)

    const activity = screen.getByRole('combobox', {
      name: /Activité principale/,
    })
    expect(activity).toHaveValue('')
    await userEvent.selectOptions(activity, 'Bibliothèque ou médiathèque')
    await waitFor(() => {
      expect(
        screen.getByText('Bibliothèque ou médiathèque')
      ).toBeInTheDocument()
    })
  })

  it('should select cultural domain', async () => {
    renderActivityForm(initialValues, contextValue)

    await userEvent.click(
      screen.getByLabelText('Sélectionnez un ou plusieurs domaines d’activité')
    )
    await waitFor(() => {
      expect(screen.getByTestId('panel-scrollable')).toBeInTheDocument()
    })
    expect(screen.getAllByText(/domaine 1/)).toHaveLength(1)
    await userEvent.click(screen.getByText(/domaine 1/))
    expect(screen.getAllByText(/domaine 1/)).toHaveLength(2)
    await userEvent.click(screen.getByText(/domaine III/))
    expect(screen.getByLabelText('domaines sélectionnés')).toBeInTheDocument()
  })
})
