import { screen } from '@testing-library/react'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { formatPhoneNumber, UserPhone } from './UserPhone'

describe('UserPhone', () => {
  it('should display the user phone form', () => {
    renderWithProviders(
      <UserPhone
        initialValues={{ phoneNumber: '' }}
        setCurrentForm={() => {}}
        showForm
      />,
      {
        user: sharedCurrentUserFactory(),
      }
    )

    expect(
      screen.getByRole('textbox', { name: 'Numéro de téléphone' })
    ).toBeInTheDocument()
  })

  it('should not display the user phone form when in mode read only', () => {
    renderWithProviders(
      <UserPhone
        initialValues={{ phoneNumber: '010203' }}
        setCurrentForm={() => {}}
        showForm={false}
      />,
      {
        user: sharedCurrentUserFactory(),
      }
    )

    expect(
      screen.queryByRole('textbox', { name: 'Numéro de téléphone' })
    ).not.toBeInTheDocument()
  })
})

describe('formatPhoneNumber', () => {
  it('should not format if the phone number is null or undefined', () => {
    expect(formatPhoneNumber(null)).toBe(null)
    expect(formatPhoneNumber(undefined)).toBe(undefined)
  })
  it('should format a phone number spaces correctly', () => {
    expect(formatPhoneNumber('0123456789')).toBe('01 23 45 67 89')
    expect(formatPhoneNumber('012 345 6789')).toBe('01 23 45 67 89')
  })

  it('should format a phone number region indicator correctly', () => {
    expect(formatPhoneNumber('+33123456789')).toBe('+33 1 23 45 67 89')
    expect(formatPhoneNumber('+33 123 456 789')).toBe('+33 1 23 45 67 89')
  })
})
