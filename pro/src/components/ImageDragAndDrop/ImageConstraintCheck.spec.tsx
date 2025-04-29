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
        errorMessage="Le format n'est pas valide"
      />
    )

    // Check that the label and constraint are rendered properly
    expect(screen.getByText('Format :')).toBeInTheDocument()
    expect(screen.getByText('JPG, PNG')).toBeInTheDocument()
  })

  it('should render error message when hasError is true', () => {
    render(
      <ImageConstraintCheck
        label="Size"
        constraint="10MB"
        hasError={true}
        errorMessage="Le fichier est trop lourd"
      />
    )

    // Ensure the error message is rendered and has the correct class
    const errorMessageElement = screen.getByText('Size :')
    expect(errorMessageElement).toBeInTheDocument()
    expect(screen.getByText('10MB')).toBeInTheDocument()

    // Ensure the error message is wrapped in a span with the error class
    const errorSpan = screen.getByText('Size :').closest('span')
    expect(errorSpan).toHaveClass(
      styles['image-drag-and-drop-description-error']
    )

    // Ensure the error message text is visually hidden (for accessibility)
    const visuallyHiddenMessage = screen.getByText('Le fichier est trop lourd')
    expect(visuallyHiddenMessage).toHaveClass(styles['visually-hidden'])
  })

  it('should not render error message when hasError is false', () => {
    render(
      <ImageConstraintCheck
        label="Dimensions"
        constraint="500px by 500px"
        hasError={false}
        errorMessage="Les dimensions sont incorrectes"
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
})
