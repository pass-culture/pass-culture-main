import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import * as useAnalytics from 'app/App/analytics/firebase'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { OffererDetails, OffererDetailsProps } from '../OffererDetails'

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useNavigate: () => mockNavigate,
}))

const renderOffererDetails = (props: Partial<OffererDetailsProps> = {}) => {
  renderWithProviders(
    <OffererDetails
      isUserOffererValidated={true}
      offererOptions={[
        {
          value: defaultGetOffererResponseModel.id,
          label: defaultGetOffererResponseModel.name,
        },
      ]}
      {...props}
    />,
    {
      storeOverrides: {
        user: {
          selectedOffererId: defaultGetOffererResponseModel.id,
          currentUser: sharedCurrentUserFactory(),
        },
      },
    }
  )
}

const mockLogEvent = vi.fn()

describe('OffererDetails', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should display offerer select', () => {
    renderOffererDetails()

    expect(
      screen.getByText(defaultGetOffererResponseModel.name)
    ).toBeInTheDocument()
  })

  it('should trigger an event when clicking on "Inviter" for offerers', async () => {
    renderOffererDetails()

    await userEvent.click(screen.getByText('Inviter'))

    expect(mockLogEvent).toHaveBeenCalledWith('hasClickedInviteCollaborator', {
      offererId: defaultGetOffererResponseModel.id,
    })
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
  })

  it('should trigger an event when clicking on "Modifier" for offerers', async () => {
    renderOffererDetails()

    await userEvent.click(screen.getByText('Modifier'))

    expect(mockLogEvent).toHaveBeenCalledWith('hasClickedModifyOfferer', {
      offerer_id: defaultGetOffererResponseModel.id,
    })
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
  })

  it('should not allow user to update offerer informations when user attachment to offerer is not yet validated', () => {
    renderOffererDetails({ isUserOffererValidated: false })

    const [offererUpdateButton] = screen.getAllByRole('link', {
      name: 'Modifier Action non disponible',
    })
    expect(offererUpdateButton).toBeInTheDocument()
  })

  it('should redirect to offerer creation page when selecting "add offerer" option"', async () => {
    renderOffererDetails()

    await userEvent.selectOptions(
      screen.getByLabelText('Structure'),
      '+ Ajouter une structure'
    )

    expect(mockNavigate).toHaveBeenCalledWith('/parcours-inscription/structure')
  })
})
