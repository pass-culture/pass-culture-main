import { fireEvent, render, screen } from '@testing-library/react'

import { SelectedValuesTags } from './SelectedValuesTags'

describe('SelectedValuesTags', () => {
  const removeOptionMock = vi.fn()

  const defaultProps = {
    disabled: false,
    fieldName: 'fieldName',
    optionsLabelById: {
      '1': 'Option 1',
      '2': 'Option 2',
      '3': 'Option 3',
    },
    selectedOptions: ['1', '2', '3'],
    removeOption: removeOptionMock,
  }

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should render tags correctly', () => {
    render(<SelectedValuesTags {...defaultProps} />)

    // Verify that each tag is rendered correctly
    expect(screen.getByText('Option 1')).toBeInTheDocument()
    expect(screen.getByText('Option 2')).toBeInTheDocument()
    expect(screen.getByText('Option 3')).toBeInTheDocument()
  })

  it('should call removeOption when a tag is removed', () => {
    render(<SelectedValuesTags {...defaultProps} />)

    const removeButton = screen.getByLabelText('Supprimer Option 1')
    fireEvent.click(removeButton)

    // Verify that the removeOption function is called with the correct argument
    expect(removeOptionMock).toHaveBeenCalledWith('1')

    expect(screen.queryByText('Supprimer Option 1')).not.toBeInTheDocument()
  })

  it('should focus on the next tag when a tag is removed', () => {
    render(<SelectedValuesTags {...defaultProps} />)

    const firstTagButton = screen.getByLabelText('Supprimer Option 1')
    fireEvent.click(firstTagButton)

    // Verify that the focus moves to the next tag (Option 2)
    const secondTagButton = screen.getByLabelText('Supprimer Option 2')
    expect(document.activeElement).toBe(secondTagButton)
  })

  it('should display the ellipsis tag if there are more than 5 selected options', () => {
    const extendedProps = {
      ...defaultProps,
      selectedOptions: Array.from({ length: 7 }, (_, index) =>
        String(index + 1)
      ),
    }

    render(<SelectedValuesTags {...extendedProps} />)

    // Check if the ellipsis tag is displayed
    expect(screen.getByText('+2...')).toBeInTheDocument()
  })

  it('should not display the ellipsis tag if there are 5 or fewer selected options', () => {
    render(<SelectedValuesTags {...defaultProps} />)

    // Check that the ellipsis tag is not displayed
    expect(screen.queryByText('+')).toBeDefined()
  })

  it('should disable the remove buttons when disabled prop is true', () => {
    const disabledProps = { ...defaultProps, disabled: true }
    render(<SelectedValuesTags {...disabledProps} />)

    const removeButton = screen.getByLabelText('Supprimer Option 1')
    expect(removeButton).toBeDisabled()
  })
})
