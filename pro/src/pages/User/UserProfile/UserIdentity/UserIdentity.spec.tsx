import { screen } from '@testing-library/react'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { UserIdentity } from './UserIdentity'

describe('UserIdentity', () => {
  it('should display the user identity form', () => {
    renderWithProviders(
      <UserIdentity
        initialValues={{ firstName: '', lastName: '' }}
        setCurrentForm={() => {}}
        showForm
      />,
      {
        user: sharedCurrentUserFactory(),
      }
    )

    expect(screen.getByRole('textbox', { name: 'Prénom' })).toBeInTheDocument()
  })

  it('should not display the user identity form when in mode read only', () => {
    renderWithProviders(
      <UserIdentity
        initialValues={{ firstName: 'Marcel', lastName: 'Pagnol' }}
        setCurrentForm={() => {}}
        showForm={false}
      />,
      {
        user: sharedCurrentUserFactory(),
      }
    )

    expect(
      screen.queryByRole('textbox', { name: 'Prénom' })
    ).not.toBeInTheDocument()
  })
})
