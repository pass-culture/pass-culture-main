import { screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { AdageCulturalPartnersResponseModel } from 'apiClient/v1'
import { renderWithProviders } from 'utils/renderWithProviders'

import { EACInformation } from '../EACInformation'

const renderEACInformation = () => renderWithProviders(<EACInformation />)

describe('components | EACInformation', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getEducationalPartners').mockResolvedValue(
      {} as AdageCulturalPartnersResponseModel
    )
  })

  it('should display EAC banner', () => {
    renderEACInformation()

    expect(screen.queryByText(/Une fois votre lieu créé/)).toBeInTheDocument()
  })
})
