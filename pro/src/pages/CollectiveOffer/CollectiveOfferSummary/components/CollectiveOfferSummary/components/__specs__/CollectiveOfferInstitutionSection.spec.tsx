import { screen } from '@testing-library/react'

import type {
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
} from '@/apiClient/v1'
import {
  defaultEducationalInstitution,
  defaultEducationalRedactor,
} from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferInstitutionSection } from '../CollectiveOfferInstitutionSection'

const renderCollectiveOfferInstitutionSection = (
  institution?: EducationalInstitutionResponseModel | null,
  teacher?: EducationalRedactorResponseModel | null
) => {
  return renderWithProviders(
    <CollectiveOfferInstitutionSection
      institution={institution}
      teacher={teacher}
    />
  )
}

describe('CollectiveOfferInstitutionSection', () => {
  it('should render all institution if no institution provided', () => {
    renderCollectiveOfferInstitutionSection()

    expect(screen.getByText('Tous les établissements')).toBeInTheDocument()
  })

  it('should render teacher informations if provided', () => {
    renderCollectiveOfferInstitutionSection(defaultEducationalInstitution, {
      ...defaultEducationalRedactor,
      firstName: 'Julien',
      lastName: 'Durand',
    })

    expect(screen.getByText('Julien Durand')).toBeInTheDocument()
  })
})
