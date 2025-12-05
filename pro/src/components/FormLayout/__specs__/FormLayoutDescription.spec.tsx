import { render, screen } from '@testing-library/react'

import {
  FormLayoutDescription,
  type FormLayoutDescriptionProps,
} from '../FormLayoutDescription'

const renderFormLayoutDescription = ({
  description,
}: FormLayoutDescriptionProps) => {
  render(<FormLayoutDescription description={description} />)
}

describe('Description', () => {
  let descriptionProps: FormLayoutDescriptionProps

  beforeEach(() => {
    descriptionProps = {
      description: 'This is a description',
    }
  })

  it('should render the description as text', () => {
    renderFormLayoutDescription(descriptionProps)
    expect(screen.getByText('This is a description')).toBeInTheDocument()
  })

  it('should not render component', () => {
    descriptionProps.description = undefined
    renderFormLayoutDescription(descriptionProps)
    expect(screen.queryByText('This is a description')).not.toBeInTheDocument()
  })
})
