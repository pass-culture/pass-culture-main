import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { TextInput } from './TextInput'

describe('TextInput', () => {
  it.each([
    'text',
    'number',
    'email',
    'url',
    'password',
    'tel',
    'search',
  ] as const)(
    'should allow tabbing from one input of type %s to the next',
    async (inputType) => {
      render(
        <>
          <TextInput type={inputType} label="Input 1" name="test1" />
          <TextInput type={inputType} label="Input 2" name="test2" />
        </>
      )

      screen.getByLabelText('Input 1 *').focus()
      expect(screen.getByLabelText('Input 1 *')).toHaveFocus()
      expect(screen.getByLabelText('Input 2 *')).not.toHaveFocus()

      await userEvent.tab()
      expect(screen.getByLabelText('Input 1 *')).not.toHaveFocus()
      expect(screen.getByLabelText('Input 2 *')).toHaveFocus()
    }
  )

  it('should link the input to its description when defined', () => {
    const inputName = 'test'
    const inputLabel = 'Ceci est un champ texte'
    const descriptionContent = 'Instructions pour le remplissage du champ.'
    const descriptionId = `description-${inputName}`

    render(
      <TextInput
        type="text"
        label={inputLabel}
        description={descriptionContent}
        name={inputName}
        isOptional={true}
      />
    )

    const description = screen.queryByTestId(descriptionId)
    expect(description).toBeInTheDocument()
    expect(description).toHaveTextContent(descriptionContent)

    const input = screen.getByRole('textbox', { name: inputLabel })
    expect(input.getAttribute('aria-describedby')).toBe(descriptionId)
  })

  it('should display the element passed as input extension when defined', () => {
    const inputExtensionContent = 'Extension content'

    render(
      <TextInput
        type="text"
        label="Input 1"
        name="test1"
        InputExtension={<span>{inputExtensionContent}</span>}
      />
    )

    expect(screen.getByText(inputExtensionContent)).toBeInTheDocument()
  })

  it('should display the element with an error', () => {
    render(
      <TextInput label="Input 1" name="test1" error="My error on my input" />
    )

    expect(screen.getByText('My error on my input')).toBeInTheDocument()
  })

  it('should ignore onKeyDown event for type number', async () => {
    render(<TextInput type="number" label="Input" name="test1" />)

    const input = screen.getByLabelText('Input *')
    await userEvent.type(input, '1000')
    await userEvent.keyboard('ArrowUp')

    expect(input).toHaveValue(1000)
  })
})
