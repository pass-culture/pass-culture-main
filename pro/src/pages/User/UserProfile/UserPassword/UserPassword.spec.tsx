import { screen } from '@testing-library/react'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { UserPassword } from './UserPassword'

describe('UserPassword', () => {
  it('should display the user password form', () => {
    renderWithProviders(<UserPassword setCurrentForm={() => {}} showForm />, {
      user: sharedCurrentUserFactory(),
    })

    expect(screen.queryByText('***************')).not.toBeInTheDocument()
  })

  it('should not display the user password form when in mode read only', () => {
    renderWithProviders(
      <UserPassword setCurrentForm={() => {}} showForm={false} />,
      {
        user: sharedCurrentUserFactory(),
      }
    )

    expect(screen.getByText('***************')).toBeInTheDocument()
  })
})
