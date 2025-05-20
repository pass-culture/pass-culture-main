import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { RadioButton } from './RadioButton'

describe('<RadioButton />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <RadioButton label="Label" name="name" value="value" />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the label and radio input (DEFAULT)', () => {
    const { getByLabelText } = render(
      <RadioButton label="Mon label" name="groupe" value="valeur" />
    )
    expect(getByLabelText('Mon label')).toBeInTheDocument()
    expect(getByLabelText('Mon label')).toHaveAttribute('type', 'radio')
  })

  it('renders the description in DETAILED variant', () => {
    const { getByText } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        variant="DETAILED"
        description="Ma description"
      />
    )
    expect(getByText('Ma description')).toBeInTheDocument()
  })

  it('renders the tag on the right in DETAILED variant', () => {
    const tag = <span data-testid="tag">TAG</span>
    const { getByTestId } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        variant="DETAILED"
        tag={tag}
      />
    )
    expect(getByTestId('tag')).toBeInTheDocument()
  })

  it('renders the icon on the right in DETAILED variant', () => {
    const { container } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        variant="DETAILED"
        icon="icon.svg"
      />
    )
    expect(container.querySelector('svg, img')).toBeInTheDocument()
  })

  it('renders the text on the right in DETAILED variant', () => {
    const { getByText } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        variant="DETAILED"
        text="19€"
      />
    )
    expect(getByText('19€')).toBeInTheDocument()
  })

  it('renders the image on the right in DETAILED variant', () => {
    const { container } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        variant="DETAILED"
        image="image.png"
        imageSize="M"
      />
    )
    expect(container.querySelector('img')).toBeInTheDocument()
    expect(container.querySelector('img')).toHaveAttribute('src', 'image.png')
  })

  it('renders collapsed only if checked', () => {
    const children = <fieldset data-testid="children">Contenu</fieldset>
    const { queryByTestId, rerender } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        variant="DETAILED"
        checked={false}
        onChange={() => {}}
        collapsed={children}
      />
    )
    expect(queryByTestId('children')).not.toBeInTheDocument()
    rerender(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        variant="DETAILED"
        checked={true}
        onChange={() => {}}
        collapsed={children}
      />
    )
    expect(queryByTestId('children')).toBeInTheDocument()
  })

  it('forwards className', () => {
    const { container } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        className="test-class"
      />
    )
    expect(container.firstChild).toHaveClass('test-class')
  })

  it('forwards additional props', () => {
    const { getByLabelText } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        data-testid="radio"
      />
    )
    expect(getByLabelText('Label')).toHaveAttribute('data-testid', 'radio')
  })

  it('handles checked state', () => {
    const { getByLabelText, rerender } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        checked={false}
        onChange={() => {}}
      />
    )
    expect(getByLabelText('Label')).not.toBeChecked()
    rerender(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        checked={true}
        onChange={() => {}}
      />
    )
    expect(getByLabelText('Label')).toBeChecked()
  })

  it('handles disabled state', () => {
    const { getByLabelText } = render(
      <RadioButton label="Label" name="groupe" value="valeur" disabled />
    )
    expect(getByLabelText('Label')).toBeDisabled()
  })

  it('calls onChange on click', () => {
    const handleChange = vi.fn()
    const { getByLabelText } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        onChange={handleChange}
      />
    )
    getByLabelText('Label').click()
    expect(handleChange).toHaveBeenCalled()
  })

  it('handles data-testid prop', () => {
    const { getByTestId } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        data-testid="custom-testid"
      />
    )

    expect(getByTestId('custom-testid')).toBeInTheDocument()
  })
})
