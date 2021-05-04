import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'

import SubmitButton from '../SubmitButton'

const renderSubmitButton = async props => {
  await act(async () => {
    await render(<SubmitButton {...props} />)
  })
}

describe('src | components | layout | SubmitButton', () => {
  let props = {
    isLoading: false,
    children: 'Enregistrer',
  }
  describe('render', () => {
    it('should display the text value of the button when is not loading and the button should be enabled', async () => {
      // When
      await renderSubmitButton(props)

      // Then
      expect(screen.getByText('Enregistrer', { selector: 'button' })).toBeEnabled()
    })

    it('should not display the text value of the button when is loading, and the button should be disabled', async () => {
      // Given
      props.isLoading = true

      // When
      await renderSubmitButton(props)

      // Then
      expect(screen.queryByText('Enregistrer', { selector: 'button' })).not.toBeInTheDocument()
      expect(screen.getByRole('button')).toBeDisabled()
    })
  })
})
