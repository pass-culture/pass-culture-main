import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { BeneficiaryBadge } from '../Components/BeneficiaryBadge'
import { PublicUserRolesEnum } from '../types'

const renderBeneficiaryBadge = props => render(<BeneficiaryBadge {...props} />)

describe('beneficiary Badge', () => {
  it('should display badge related to role', () => {
    // Given
    const props = {
      role: PublicUserRolesEnum.beneficiary,
    }
    const expectedLabel = 'Pass 18'

    // When
    renderBeneficiaryBadge(props)

    // Then
    expect(screen.getByText(expectedLabel)).toBeInTheDocument()
  })
})
