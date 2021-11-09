import { screen } from '@testing-library/react'

export const getCategoriesSelect = (): HTMLSelectElement => 
    screen.getByLabelText('Domaine') as HTMLSelectElement

export const getSubcategoriesSelect = (): HTMLSelectElement =>
    screen.getByLabelText('Sous Domaine') as HTMLSelectElement
