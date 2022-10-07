import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import {
  BankAccountStatusBadge,
  BankAccountStatusBadgeProps,
} from '../Components/BankAccountStatusBadge'

const renderBankAccountStatusBadge = (props: BankAccountStatusBadgeProps) =>
  render(<BankAccountStatusBadge {...props} />)

describe('bank account status badge', () => {
  it('should display success badge related to bank account status', () => {
    //Given
    const props = {
      OK: 1,
      KO: 0,
    }
    const expectedIcon = 'CheckCircleOutlineIcon'

    //When
    renderBankAccountStatusBadge(props)

    //Then
    expect(screen.getByTestId(expectedIcon)).toBeInTheDocument()
  })
  it('should display error badge related to bank account status', () => {
    //Given
    const props = {
      OK: 0,
      KO: 1,
    }
    const expectedIcon = 'HighlightOffIcon'

    //When
    renderBankAccountStatusBadge(props)

    //Then
    expect(screen.getByTestId(expectedIcon)).toBeInTheDocument()
  })
  it('should display warning badge related to bank account status', () => {
    //Given
    const props = {
      OK: 1,
      KO: 1,
    }
    const expectedIcon = 'WarningIcon'

    //When
    renderBankAccountStatusBadge(props)

    //Then
    expect(screen.getByTestId(expectedIcon)).toBeInTheDocument()
  })
})
