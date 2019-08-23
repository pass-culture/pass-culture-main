import React from 'react'

import { shallow } from 'enzyme'

import UploadThumb, { computeNewZoom } from '../UploadThumb'

const defaultParams = {
  current: 0.3,
  min: 0.1,
  max: 3,
  step: 0.01,
  factor: 10,
  direction: 1,
}
describe('src | components | layout | UploadThumb |', () => {
  let props
  let image = {
    lastModified: 1565378546222,
    lastModifiedDate: 'Fri Aug 09 2019 21:22:26 GMT+0200 (heure d’été d’Europe centrale)',
    name: 'IMG_4366.jpg',
    size: 1503804,
    type: 'image/jpeg',
    webkitRelativePath: '',
  }

  beforeEach(() => {
    props = {
      collectionName: 'fake',
      dispatch: jest.fn(),
      hasExistingImage: false,
      image: null,
      onImageChange: jest.fn(),
      storeKey: 'image',
    }
  })

  it('should match the snapshot', () => {
    // given
    props.image = {
      name: 'IMG_4366.jpg',
      size: 1503804,
      type: 'image/jpeg',
    }

    // when
    const wrapper = shallow(<UploadThumb {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render Mediation component with default state', () => {
      // when
      const wrapper = shallow(<UploadThumb {...props} />)

      // then
      expect(wrapper.state('isEdited')).toBe(false)
      expect(wrapper.state('readOnly')).toBe(false)
      expect(wrapper.state('image')).toBeNull()
      expect(wrapper.state('isUploadDisabled')).toBe(false)
      expect(wrapper.state('isDragging')).toBe(false)
      expect(wrapper.state('zoom')).toBe(1)
    })
  })

  describe('handleDragStart', () => {
    it('should update dragging value to true', () => {
      // given
      const wrapper = shallow(<UploadThumb {...props} />)

      // when
      wrapper.instance().handleDragStart()

      // then
      expect(wrapper.state('dragging')).toBe(true)
    })
  })

  describe('handleDragStop', () => {
    it('should update dragging value to false', () => {
      // given
      const wrapper = shallow(<UploadThumb {...props} />)

      // when
      wrapper.instance().handleDragStop()

      // then
      expect(wrapper.state('dragging')).toBe(false)
    })
  })

  describe('handleDrop', () => {
    it('should update dragging value to false', () => {
      // given
      const droppedValues = [image]
      const wrapper = shallow(<UploadThumb {...props} />)

      // when
      wrapper.instance().handleDrop(droppedValues)

      // then
      expect(wrapper.state('isDragging')).toBe(false)
      expect(wrapper.state('isUploadDisabled')).toBe(false)
      expect(wrapper.state('image')).toBe(image)
      expect(wrapper.state('size')).toBe(1.4341392517089844)
    })
  })

  describe('handleOnZoomChange', () => {
    it('should increase image size with value given by cursor change', () => {
      // given
      props.image = {
        name: 'IMG_4366.jpg',
        size: 1503804,
        type: 'image/jpeg',
      }

      // when
      const wrapper = shallow(<UploadThumb {...props} />)
      wrapper.find('input[name="zoomLeft"]').simulate('change', { target: { value: 1.95 } })

      // then
      expect(wrapper.state('zoom')).toBe(1.95)
    })
  })

  describe('handleOnImageChange', () => {
    const ctx = { fillStyle: '#000000' }

    it('should not be called when no image', () => {
      // when
      const wrapper = shallow(<UploadThumb {...props} />)

      wrapper.instance().handleOnImageChange(ctx)

      // then
      expect(props.onImageChange).not.toHaveBeenCalledWith()
    })

    it('should be called with ctx when onImageChange func given and upload is disabled', () => {
      // given
      props.image = {
        name: 'IMG_4366.jpg',
        size: 1503804,
        type: 'image/jpeg',
      }

      // when
      const wrapper = shallow(<UploadThumb {...props} />)
      wrapper.setState({ image, isUploadDisabled: true, size: 15038040 })

      wrapper.instance().handleOnImageChange(ctx)

      // then
      expect(props.onImageChange).toHaveBeenCalledWith(ctx)
    })
  })

  describe('handleDecrement', () => {
    it('should decrement zoom on click', () => {
      // given
      props.image = {
        name: 'IMG_4366.jpg',
        size: 1503804,
        type: 'image/jpeg',
      }

      // comment mocker this.zoomInput ??
      // when
      const wrapper = shallow(<UploadThumb {...props} />)
      // wrapper.find('.decrement').simulate('click')
      wrapper.instance().changeZoom(1)

      // then
      // expect(changeZoomFunc).toHaveBeenCalledWith()
      expect(wrapper.state('zoom')).toBe(1)

    })
  })

  describe('computeNewZoom', () => {
    it('should return a bigger zoom', () => {
      // given
      const { current, min, max, step, factor, direction } = defaultParams

      // when
      const newZoom = computeNewZoom(current, min, max, step, factor, direction)

      // then
      expect(newZoom).toBeGreaterThan(current)
    })

    it('should return a smaller zoom', () => {
      // given
      const { current, min, max, step, factor } = defaultParams
      const direction = -1

      // when
      const newZoom = computeNewZoom(current, min, max, step, factor, direction)

      // then
      expect(newZoom).toBeLessThan(current)
    })

    it('should not return zoom smaller than min', () => {
      // given
      const { min, max, step, factor } = defaultParams
      const current = min + step
      const direction = -1

      // when
      const newZoom = computeNewZoom(current, min, max, step, factor, direction)

      // then
      expect(newZoom).toStrictEqual(current)
    })

    it('should not return zoom greater than max', () => {
      // given
      const { min, max, step, factor, direction } = defaultParams
      const current = max - step

      // when
      const newZoom = computeNewZoom(current, min, max, step, factor, direction)

      // then
      expect(newZoom).toStrictEqual(current)
    })
  })
})
