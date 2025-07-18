import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { TagVariant } from 'design-system/Tag/Tag'

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
        variant="detailed"
        description="Ma description"
      />
    )
    expect(getByText('Ma description')).toBeInTheDocument()
  })

  it('not renders any asset in DEFAULT variant', () => {
    const { container } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        variant="default"
        asset={{
          variant: 'icon',
          src: 'icon.svg',
        }}
      />
    )

    expect(container.querySelector('svg, img')).not.toBeInTheDocument()
  })

  it('renders the tag on the right in DETAILED variant', () => {
    const { getByText } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        variant="detailed"
        asset={{
          variant: 'tag',
          tag: {
            label: 'Tag',
            variant: TagVariant.SUCCESS,
          },
        }}
      />
    )
    expect(getByText('Tag')).toBeInTheDocument()
  })

  it('renders the icon on the right in DETAILED variant', () => {
    const { container } = render(
      <RadioButton
        label="Label"
        name="groupe"
        value="valeur"
        variant="detailed"
        asset={{
          variant: 'icon',
          src: 'icon.svg',
        }}
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
        variant="detailed"
        asset={{ variant: 'text', text: '19€' }}
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
        variant="detailed"
        asset={{ variant: 'image', src: 'image.png', size: 'm' }}
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
        variant="detailed"
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
        variant="detailed"
        checked={true}
        onChange={() => {}}
        collapsed={children}
      />
    )
    expect(queryByTestId('children')).toBeInTheDocument()
  })

  it('handles disabled state', () => {
    const { getByLabelText } = render(
      <RadioButton label="Label" name="groupe" value="valeur" disabled />
    )
    expect(getByLabelText('Label')).toBeDisabled()
  })

  it('handles error state', () => {
    const { getByLabelText } = render(
      <RadioButton label="Label" name="groupe" value="valeur" hasError />
    )
    const radio = getByLabelText('Label')
    expect(radio).toHaveAttribute('aria-invalid', 'true')
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
})
