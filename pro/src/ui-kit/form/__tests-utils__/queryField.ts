import { screen, within } from '@testing-library/react'

const contains = (str: string): RegExp => new RegExp(`^${str}.*$`, 'i')

export type QueryFieldResponse<T> = {
  input: T | null
  wrapper: HTMLElement | null
  isOptionnal: boolean
  getCounter(): HTMLElement | null
  getError(): HTMLElement | null
}

export const queryField = <
  T extends HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
>(
  label: string
): QueryFieldResponse<T> => {
  const input = screen.queryByLabelText(contains(label)) as T | null

  if (!input) {
    return {
      input: null,
      wrapper: null,
      isOptionnal: false,
      getError: () => null,
      getCounter: () => null,
    }
  }

  const fieldName = input.getAttribute('id')
  const wrapper = screen.getByTestId(`wrapper-${fieldName}`)
  const isOptionnal = !!within(wrapper).queryByText(contains('Optionnel'))

  return {
    input,
    wrapper,
    isOptionnal,
    getError: () => within(wrapper).queryByTestId(`error-${fieldName}`),
    getCounter: () => within(wrapper).queryByTestId(`counter-${fieldName}`),
  }
}
