import { screen } from '@testing-library/react'

export const getResetFiltersButton = (): HTMLElement | null =>
  screen.queryByRole('button', {
    name: 'Réinitialiser les filtres',
  })

export const getDepartmentFilter = async (): Promise<HTMLElement> =>
  screen.findByLabelText('Département', {
    selector: 'input',
  })

export const getStudentsFilter = async (): Promise<HTMLElement> =>
  screen.findByLabelText('Niveau scolaire', {
    selector: 'input',
  })

export const getLaunchSearchButton = async (): Promise<HTMLElement> =>
  screen.findByRole('button', {
    name: 'Lancer la recherche',
  })
