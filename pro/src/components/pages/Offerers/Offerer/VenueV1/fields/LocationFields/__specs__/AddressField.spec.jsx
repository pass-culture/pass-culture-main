import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

import { addressFieldRender } from '../AddressField'

describe('src | components | pages | Venue | fields | AddressField', () => {
  describe('addressFieldRender', () => {
    let props
    let input
    let meta

    beforeEach(() => {
      props = {
        className: 'fake className',
        disabled: true,
        form: {},
        id: 'test-id',
        innerClassName: 'fake inner className',
        label: 'fake label',
        name: 'fake name',
        placeholder: 'fake placeholder',
        readOnly: true,
        required: true,
        AddressProps: {},
      }
      input = {}
      meta = {}
    })

    it('should display a div with the right props', () => {
      // when
      render(addressFieldRender({ ...props })({ input, meta }))
      // then
      expect(screen.getByText('fake label')).toBeInTheDocument()
    })

    it('should display the label and the required asterisk sign when not read only mode and label is provided', () => {
      // given
      props.readOnly = false

      // when
      render(addressFieldRender({ ...props })({ input, meta }))

      // then
      expect(screen.getByText('fake label')).toBeInTheDocument()
      expect(screen.getByText('*')).toBeInTheDocument()
    })

    it('should display a LocationViewer component with the right props when readOnly', () => {
      // when

      render(addressFieldRender({ ...props })({ input, meta }))
      // then
      const locationViewer = screen.getByRole('textbox')
      expect(locationViewer).toHaveAttribute('readOnly')
      expect(locationViewer).not.toHaveAttribute('disabled')
      expect(locationViewer).not.toHaveAttribute('required')
      expect(locationViewer).toHaveAttribute('name', 'fake name')
      expect(locationViewer).toHaveClass('field-input', 'field-address')
    })

    it('should display a LocationViewer component with the right props when not disabled, not read only mode, not required', () => {
      // given
      props.readOnly = false
      props.disabled = false
      props.required = false

      // when
      render(addressFieldRender({ ...props })({ input, meta }))

      // then
      const locationViewer = screen.getByRole('combobox')
      expect(locationViewer).not.toHaveAttribute('disabled')
      expect(locationViewer).not.toHaveAttribute('readOnly')
      expect(locationViewer).not.toHaveAttribute('required')
      expect(locationViewer).toHaveAttribute('name', 'fake name')
      expect(locationViewer).toHaveAttribute('placeholder', 'fake placeholder')
      expect(locationViewer).toHaveClass('field-input', 'field-address')
    })

    it('should display a FieldErrors component with the right props', () => {
      // when
      meta = { error: 'Custom error', touched: true }
      render(addressFieldRender({ ...props })({ input, meta }))
      expect(screen.getByText('Custom error')).toBeInTheDocument()
    })
  })
})
