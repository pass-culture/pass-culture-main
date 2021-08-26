/*
* @debt complexity "Gaël: file nested too deep in directory structure"
*/

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import BeneficiaryCell from '../BeneficiaryCell'

const renderBeneficiaryCell = props => render(<BeneficiaryCell {...props} />)

describe('bookings beneficiary cell', () => {
  it('should display an user firstname, lastname and email address', () => {
    // Given
    const props = {
      beneficiaryInfos: {
        firstname: 'Laurent',
        lastname: 'Durond',
        email: 'laurentdurond@example.com',
      },
    }

    // When
    renderBeneficiaryCell(props)

    // Then
    expect(screen.getByText('Durond Laurent')).toBeInTheDocument()
    expect(screen.getByText('laurentdurond@example.com')).toBeInTheDocument()
  })
})
