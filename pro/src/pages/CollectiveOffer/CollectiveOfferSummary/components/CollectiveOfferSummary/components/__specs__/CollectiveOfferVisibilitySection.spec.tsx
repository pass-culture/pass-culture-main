import { screen } from '@testing-library/react'

import {
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
} from '@/apiClient//v1'
import {
  defaultEducationalInstitution,
  defaultEducationalRedactor,
} from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferVisibilitySection } from '../CollectiveOfferVisibilitySection'

const renderCollectiveOfferVisibilitySection = (
  institution?: EducationalInstitutionResponseModel | null,
  teacher?: EducationalRedactorResponseModel | null
) => {
  return renderWithProviders(
    <CollectiveOfferVisibilitySection
      institution={institution}
      teacher={teacher}
    />
  )
}

describe('CollectiveOfferVisibilitySection', () => {
  it('should render all institution if no institution provided', () => {
    renderCollectiveOfferVisibilitySection()

    expect(screen.getByText('Tous les établissements')).toBeInTheDocument()
  })

  it('should render teacher informations if provided', () => {
    renderCollectiveOfferVisibilitySection(defaultEducationalInstitution, {
      ...defaultEducationalRedactor,
      firstName: 'Julien',
      lastName: 'Durand',
    })

    expect(screen.getByText('Julien Durand')).toBeInTheDocument()
  })
})
