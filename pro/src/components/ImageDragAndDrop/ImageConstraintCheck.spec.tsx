import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ImageConstraintCheck } from './ImageConstraintCheck' // Import your component
import styles from './ImageDragAndDrop.module.scss' // Import the styles

describe('ImageConstraintCheck', () => {
  it('should render label and constraint correctly', () => {
    render(
      <ImageConstraintCheck
        label="Format"
        constraint="JPG, PNG"
        hasError={false}
        hasInput={true}
      />
    )

    // Check that the label and constraint are rendered properly
    expect(screen.getByText('Format :')).toBeInTheDocument()
    expect(screen.getByText('JPG, PNG')).toBeInTheDocument()
  })

  it('should render in error state when hasError is true', () => {
    render(
      <ImageConstraintCheck
        label="Size"
        constraint="10MB"
        hasError={true}
        hasInput={true}
      />
    )

    // Ensure the error message is rendered and has the correct class
    const errorMessageElement = screen.getByText('Size :')
    expect(errorMessageElement).toBeInTheDocument()
    expect(screen.getByText('10MB')).toBeInTheDocument()

    // Ensure the error message is wrapped in a container with the error class
    const errorContainer = screen.getByText('Size :').closest('div')
    expect(errorContainer).toHaveClass(
      styles['image-drag-and-drop-description-error']
    )
  })

  it('should not render error message when hasError is false', () => {
    render(
      <ImageConstraintCheck
        label="Dimensions"
        constraint="500px by 500px"
        hasError={false}
        hasInput={true}
      />
    )

    // Ensure no error message is rendered and the component does not have the error class
    const errorSpan = screen.queryByText('Dimensions :')
    expect(errorSpan).not.toHaveClass(
      styles['image-drag-and-drop-description-error']
    )

    // Ensure the error message is not visible
    const visuallyHiddenMessage = screen.queryByText(
      'Les dimensions sont incorrectes'
    )
    expect(visuallyHiddenMessage).not.toBeInTheDocument()
  })

  it('should render in valid state with hasInput is true and hasError is false', () => {
    render(
      <ImageConstraintCheck
        label="Format"
        constraint="JPG, PNG"
        hasError={false}
        hasInput={true}
      />
    )

    const validateContainer = screen.getByText('Format :').closest('div')
    expect(validateContainer).toHaveClass(
      styles['image-drag-and-drop-description-validate']
    )
  })

  it('should render neutral state when hasInput is false', () => {
    render(
      <ImageConstraintCheck
        label="Format"
        constraint="JPG, PNG"
        hasError={false}
        hasInput={false}
      />
    )

    const neutralSpan = screen.getByText('Format :').closest('p')
    expect(neutralSpan).toHaveClass(
      styles['image-drag-and-drop-description-neutral']
    )

    expect(screen.queryByText('Valide :')).not.toBeInTheDocument()
    expect(
      screen.queryByText("Le format n'est pas valide")
    ).not.toBeInTheDocument()
  })
})
