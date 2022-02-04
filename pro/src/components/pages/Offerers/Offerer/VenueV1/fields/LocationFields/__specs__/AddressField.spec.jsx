import { shallow } from 'enzyme'

import FieldErrors from 'components/layout/form/FieldErrors'

import { addressFieldRender } from '../AddressField'
import LocationViewer from '../LocationViewer'

describe('src | components | pages | Venue | fields | AddressField', () => {
  describe('addressFieldRender', () => {
    let props
    let input
    let meta

    beforeEach(() => {
      props = {
        className: 'fake className',
        disabled: false,
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
      const wrapper = shallow(addressFieldRender({ ...props })({ input, meta }))

      // then
      const mainDiv = wrapper.find('div').first()
      expect(mainDiv.prop('className')).toBe(
        'field text-field fake className is-label-aligned is-read-only'
      )
      expect(mainDiv.prop('id')).toBe('test-id-container')
    })

    it('should display the label and the required asterisk sign when not read only mode and label is provided', () => {
      // given
      props.readOnly = false

      // when
      const wrapper = shallow(addressFieldRender({ ...props })({ input, meta }))

      // then
      const label = wrapper.find('label')
      expect(label.prop('htmlFor')).toBe('fake name')
      expect(label.prop('className')).toBe('field-label')
      const spans = label.find('span')
      expect(spans).toHaveLength(3)
      expect(spans.at(1).text()).toBe('fake label')
      expect(spans.at(2).prop('className')).toBe('field-asterisk')
      expect(spans.at(2).text()).toBe('*')
    })

    it('should display a LocationViewer component with the right props when disabled, read only mode, required', () => {
      // when
      const wrapper = shallow(addressFieldRender({ ...props })({ input, meta }))

      // then
      const locationViewer = wrapper.find(LocationViewer)
      expect(locationViewer).toHaveLength(1)
      expect(locationViewer.prop('className')).toBe('field-input field-address')
      expect(locationViewer.prop('disabled')).toBe(true)
      expect(locationViewer.prop('name')).toBe('fake name')
      expect(locationViewer.prop('onMarkerDragend')).toStrictEqual(
        expect.any(Function)
      )
      expect(locationViewer.prop('onSuggestionSelect')).toStrictEqual(
        expect.any(Function)
      )
      expect(locationViewer.prop('onTextChange')).toStrictEqual(
        expect.any(Function)
      )
      expect(locationViewer.prop('placeholder')).toBe('')
      expect(locationViewer.prop('readOnly')).toBe(true)
      expect(locationViewer.prop('required')).toBe(true)
    })

    it('should display a LocationViewer component with the right props when not disabled, not read only mode, not required', () => {
      // given
      props.readOnly = false
      props.disabled = false
      props.required = false

      // when
      const wrapper = shallow(addressFieldRender({ ...props })({ input, meta }))

      // then
      const locationViewer = wrapper.find(LocationViewer)
      expect(locationViewer).toHaveLength(1)
      expect(locationViewer.prop('className')).toBe('field-input field-address')
      expect(locationViewer.prop('disabled')).toBe(false)
      expect(locationViewer.prop('name')).toBe('fake name')
      expect(locationViewer.prop('onMarkerDragend')).toStrictEqual(
        expect.any(Function)
      )
      expect(locationViewer.prop('onSuggestionSelect')).toStrictEqual(
        expect.any(Function)
      )
      expect(locationViewer.prop('onTextChange')).toStrictEqual(
        expect.any(Function)
      )
      expect(locationViewer.prop('placeholder')).toBe('fake placeholder')
      expect(locationViewer.prop('readOnly')).toBe(false)
      expect(locationViewer.prop('required')).toBe(false)
    })

    it('should display a FieldErrors component with the right props', () => {
      // when
      const wrapper = shallow(addressFieldRender({ ...props })({ input, meta }))

      // then
      const fieldErrors = wrapper.find(FieldErrors)
      expect(fieldErrors.prop('meta')).toStrictEqual({})
    })
  })
})
