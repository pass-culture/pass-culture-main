import { screen } from '@testing-library/react'

export const queryResetFiltersButton = (): HTMLElement | null =>
  screen.queryByRole('button', {
    name: 'Réinitialiser les filtres',
  })
export const findDepartmentFilter = (): Promise<HTMLElement> =>
  screen.findByLabelText('Département', {
    selector: 'input',
  })
export const findStudentsFilter = (): Promise<HTMLElement> =>
  screen.findByLabelText('Niveau scolaire', {
    selector: 'input',
  })
export const findLaunchSearchButton = (): Promise<HTMLElement> =>
  screen.findByRole('button', {
    name: 'Lancer la recherche',
  })
