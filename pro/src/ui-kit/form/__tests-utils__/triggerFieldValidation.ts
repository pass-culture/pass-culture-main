import userEvent from '@testing-library/user-event'

export const triggerFieldValidation = (
  input: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
): void => {
  userEvent.click(input)
  userEvent.tab()
}
