import { screen } from '@testing-library/react'

export const getOfferTypePageElements = (): {
  educationalOfferButton: HTMLInputElement,
  submitButton: HTMLButtonElement,
} => ({
  educationalOfferButton: screen.getByLabelText("Une offre à destination d'un groupe scolaire") as HTMLInputElement,
  submitButton: screen.getByRole('button') as HTMLButtonElement,
})