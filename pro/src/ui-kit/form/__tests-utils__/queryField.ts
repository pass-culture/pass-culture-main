import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

const contains = (str: string): RegExp => new RegExp(`^${str}.*$`, 'i')

const stringWithCharCount = (count: number): string =>
  new Array(count).fill('x').join('')

export type QueryFieldResponse<T> = {
  input: T | null
  wrapper: HTMLElement | null
  isOptionnal: boolean
  getCounter(): HTMLElement | null
  getError(): HTMLElement | null
  doesTruncateAt(charCount: number): Promise<boolean>
}

export const queryField = async <
  T extends HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
>(
  label: string
): Promise<QueryFieldResponse<T>> => {
  const input = screen.queryByLabelText(contains(label)) as T | null

  if (!input) {
    return {
      input: null,
      wrapper: null,
      isOptionnal: false,
      getError: () => null,
      getCounter: () => null,
      doesTruncateAt: async () => false,
    }
  }

  const fieldName = input.getAttribute('id')
  const wrapper = screen.getByTestId(`wrapper-${fieldName}`)
  const isOptionnal = !!within(wrapper).queryByText(contains('Optionnel'))
  const getError = () => within(wrapper).queryByTestId(`error-${fieldName}`)
  const getCounter = () => within(wrapper).queryByTestId(`counter-${fieldName}`)

  const doesTruncateAt = async (charCount: number) => {
    const tooLongString = stringWithCharCount(charCount + 10)
    const expectedTruncatedString = stringWithCharCount(charCount)

    await userEvent.clear(input as T)
    await userEvent.type(input as T, tooLongString)

    await within(wrapper).findByText(`${charCount}/${charCount}`)

    const isValid = input.value.length === expectedTruncatedString.length

    // clean input and wait for last update
    await userEvent.clear(input as T)
    await within(wrapper).findByDisplayValue('')

    return isValid
  }

  return {
    input,
    wrapper,
    isOptionnal,
    getError,
    getCounter,
    doesTruncateAt,
  }
}
