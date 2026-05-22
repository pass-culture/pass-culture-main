import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import type { SWRResponse } from 'swr'
import { vi } from 'vitest'

import * as useEducationalDomains from '@/commons/hooks/swr/useEducationalDomains'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ActivityDetails } from './ActivityDetails'

type FormValues = {
  activity: string | null
  isOpenToPublic: string
  culturalDomains: string[]
  description: string
}

const renderActivityDetails = ({
  isOpenToPublic = 'true',
  activity = null,
  culturalDomains = [],
  isVenueVirtual = false,
}: {
  isOpenToPublic?: string
  activity?: string | null
  culturalDomains?: string[]
  isVenueVirtual?: boolean
} = {}) => {
  const Wrapper = () => {
    const form = useForm<FormValues>({
      defaultValues: {
        isOpenToPublic,
        activity,
        culturalDomains,
        description: '',
      },
    })
    return (
      <FormProvider {...form}>
        <ActivityDetails isVenueVirtual={isVenueVirtual} />
      </FormProvider>
    )
  }
  return renderWithProviders(<Wrapper />)
}

describe('ActivityDetails', () => {
  beforeEach(() => {
    vi.spyOn(useEducationalDomains, 'useEducationalDomains').mockReturnValue({
      isLoading: false,
      data: [
        { id: 1, name: 'domaine 1', nationalPrograms: [] },
        { id: 2, name: 'domaine b', nationalPrograms: [] },
        { id: 3, name: 'domaine III', nationalPrograms: [] },
      ],
    } as SWRResponse)
  })

  describe('activity select', () => {
    it('should show a placeholder option when activity is null', async () => {
      renderActivityDetails({ activity: null })

      const activitySelect = await screen.findByLabelText(/Activité principale/)
      expect(activitySelect).toHaveValue('')
      expect(
        screen.getByText('Sélectionnez votre activité principale')
      ).toBeInTheDocument()
      expect(activitySelect).not.toBeDisabled()
    })

    it('should display the proper activities list for structures open to public', async () => {
      renderActivityDetails({ isOpenToPublic: 'true' })

      const activitySelect = await screen.findByRole('combobox', {
        name: /Activité principale/,
      })
      ;['Librairie', 'Cinéma', 'Centre socio-culturel'].forEach((label) => {
        expect(
          within(activitySelect).getByRole('option', { name: label })
        ).toBeInTheDocument()
      })
    })

    it('should display the proper activities list for structures not open to public', async () => {
      renderActivityDetails({ isOpenToPublic: 'false' })

      const activitySelect = await screen.findByRole('combobox', {
        name: /Activité principale/,
      })
      ;[
        'Société de production, tourneur ou label',
        'Presse ou média',
        'Cinéma itinérant',
      ].forEach((label) => {
        expect(
          within(activitySelect).getByRole('option', { name: label })
        ).toBeInTheDocument()
      })
    })

    it('should be disabled for virtual venues', async () => {
      renderActivityDetails({ isVenueVirtual: true })

      const activitySelect = await screen.findByLabelText(/Activité principale/)
      expect(activitySelect).toBeDisabled()
    })
  })

  describe('cultural domains', () => {
    it('should render the multi-select with all available options', async () => {
      renderActivityDetails()

      const multiSelect = screen.getByLabelText(
        "Sélectionnez un ou plusieurs domaines d'activité"
      )
      expect(multiSelect).toBeInTheDocument()
      await userEvent.click(multiSelect)
      await waitFor(() => {
        expect(screen.getByTestId('panel-scrollable')).toBeInTheDocument()
      })
      expect(screen.getByText(/3 résultats trouvés/)).toBeInTheDocument()
      expect(screen.getByText('domaine III')).toBeInTheDocument()
    })

    it('should pre-select domains from default form values', async () => {
      renderActivityDetails({ culturalDomains: ['domaine 1'] })

      await userEvent.click(screen.getByLabelText('domaine sélectionné'))
      await waitFor(() => {
        expect(screen.getByTestId('panel-scrollable')).toBeInTheDocument()
      })
      expect(screen.getAllByText(/domaine 1/)).toHaveLength(2)
    })

    it('should allow selecting multiple cultural domains', async () => {
      renderActivityDetails()

      await userEvent.click(
        screen.getByLabelText(
          "Sélectionnez un ou plusieurs domaines d'activité"
        )
      )
      await waitFor(() => {
        expect(screen.getByTestId('panel-scrollable')).toBeInTheDocument()
      })
      await userEvent.click(screen.getByText('domaine 1'))
      await userEvent.click(screen.getByText('domaine III'))
      expect(screen.getByLabelText('domaines sélectionnés')).toBeInTheDocument()
    })
  })
})
