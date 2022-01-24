import { screen } from '@testing-library/react'

export const queryResetFiltersButton = (): HTMLElement | null =>
  screen.queryByRole('button', {
    name: 'Réinitialiser les filtres',
  })

export const findDepartmentFilter = (): Promise<HTMLElement> =>
  screen.findByLabelText('Département')

export const findStudentsFilter = (): Promise<HTMLElement> =>
  screen.findByLabelText('Niveau scolaire')

export const findCategoriesFilter = (): Promise<HTMLElement> =>
  screen.findByLabelText('Catégorie')

export const findLaunchSearchButton = (): Promise<HTMLElement> =>
  screen.findByRole('button', {
    name: 'Lancer la recherche',
  })
export const queryTag = (tagName: string): HTMLElement | null =>
  screen.queryByText(tagName, { selector: 'div' })
