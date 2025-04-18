import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ForwardedRef } from 'react'

import * as useAnalytics from 'app/App/analytics/firebase'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { TextArea, TextAreaProps } from './TextArea'

const defaultProps: TextAreaProps = {
  label: 'Label',
  name: 'area',
}

function rednerTextArea(props?: Partial<ForwardedRef<TextAreaProps>>) {
  renderWithProviders(
    <TextArea {...defaultProps} {...(props as TextAreaProps)} />
  )
}

describe('TextArea', () => {
  it('should show an textarea with a label', () => {
    rednerTextArea()

    expect(screen.getByLabelText('Label')).toBeInTheDocument()
  })

  it('should show the characters count', () => {
    rednerTextArea({ value: 'Bonjour', maxLength: 100 })

    expect(screen.getByText('7/100')).toBeInTheDocument()
  })

  it('should show the an error message', () => {
    rednerTextArea({ error: 'Error message' })

    expect(screen.getByText('Error message')).toBeInTheDocument()
  })

  it('should fill the textarea with the collective custom template', async () => {
    vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
      AB_COLLECTIVE_DESCRIPTION_TEMPLATE: 'true',
    })

    rednerTextArea({
      hasTemplateButton: true,
      wordingTemplate: 'Test template',
      onPressTemplateButton: () => {},
      ref: { current: 'value' },
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Générer un modèle' })
    )

    expect(screen.getByRole('textbox')).toHaveValue('Test template')
  })
})
