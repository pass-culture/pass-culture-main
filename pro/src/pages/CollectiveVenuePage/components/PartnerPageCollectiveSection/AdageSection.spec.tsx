import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { TagVariant } from '@/design-system/Tag/Tag'

import { AdageSection } from './AdageSection'

describe('AdageSection', () => {
  it('should display the status prefix and the tag label', () => {
    renderWithProviders(
      <AdageSection
        tagText="Référencé dans ADAGE"
        variant={TagVariant.SUCCESS}
      />
    )

    expect(screen.getByText(/État auprès des enseignants/)).toBeVisible()
    expect(screen.getByText('Référencé dans ADAGE')).toBeVisible()
  })

  it('should display the description when provided', () => {
    renderWithProviders(
      <AdageSection
        tagText="Non référencé dans ADAGE"
        variant={TagVariant.DEFAULT}
        description={<p>Une description</p>}
      />
    )

    expect(screen.getByText('Une description')).toBeVisible()
  })

  it('should not display any description when none is provided', () => {
    renderWithProviders(
      <AdageSection
        tagText="Référencé dans ADAGE"
        variant={TagVariant.SUCCESS}
      />
    )

    expect(screen.queryByText('Une description')).not.toBeInTheDocument()
  })

  it('should render its children', () => {
    renderWithProviders(
      <AdageSection
        tagText="Référencement en cours"
        variant={TagVariant.WARNING}
      >
        <button>Déposer un dossier ADAGE</button>
      </AdageSection>
    )

    expect(
      screen.getByRole('button', { name: 'Déposer un dossier ADAGE' })
    ).toBeVisible()
  })
})
