import React from 'react'

import { shallow } from 'enzyme'

import UploadThumb, { computeNewZoom, isImageTooLarge } from '../UploadThumb'

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
      image,
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
    it('should render main component with default state', () => {
      // when
      const wrapper = shallow(<UploadThumb {...props} />)

      // then
      expect(wrapper.state('readOnly')).toBe(false)
      expect(wrapper.state('image')).toStrictEqual(image)
      expect(wrapper.state('isUploadDisabled')).toBe(false)
      expect(wrapper.state('zoom')).toBe(1)
    })

    describe('editor-zone div', () => {
      it('should render main component properly', () => {
        // given
        const wrapper = shallow(<UploadThumb {...props} />)

        // when
        const editorZoneComponent = wrapper.find('.editor-zone')

        // then
        expect(editorZoneComponent).toHaveLength(1)
      })

      it('should not have no-drag class when is readOnly', () => {
        // given
        props.image = {
          name: 'editor-zoneExample.jpg',
          size: 1503804,
          type: 'image/jpeg',
        }
        props.hasExistingImage = true

        // when
        const wrapper = shallow(<UploadThumb {...props} />)
        const editorZoneComponent = wrapper.find('.editor-zone')

        // then
        expect(editorZoneComponent.props().className).toStrictEqual('editor-zone has-image no-drag')
      })
    })

    describe('image too large alert message', () => {
      it('should not be displayed when image is smaller', () => {
        // when
        const wrapper = shallow(<UploadThumb {...props} />)
        const showAlertComponent = wrapper.find('.has-text-danger')

        // then
        expect(showAlertComponent).toHaveLength(0)
      })

      it('should not be displayed when image is larger', () => {
        // given
        props.image = {
          name: 'editor-zoneExample.jpg',
          size: 150380467,
          type: 'image/jpeg',
        }
        props.hasExistingImage = true

        // when
        const wrapper = shallow(<UploadThumb {...props} />)
        const showAlertComponent = wrapper.find('.has-text-danger')

        // then
        expect(showAlertComponent.text()).toStrictEqual(
          'Votre image trop volumineuse : 150.380467 > 10 Mo'
        )
      })
    })

    describe('zoomcontrol', () => {
      it('should not be displayed when image is uploaded', () => {
        // given
        props.hasExistingImage = true

        // when
        const wrapper = shallow(<UploadThumb {...props} />)

        const zoomControlComponent = wrapper.find('#zoomControl')

        // then
        expect(zoomControlComponent).toHaveLength(0)
      })

      it('should be displayed when image is uploaded', () => {
        // given
        props.hasExistingImage = false

        // when
        const wrapper = shallow(<UploadThumb {...props} />)

        const zoomControlComponent = wrapper.find('#zoomControl')

        // then
        expect(zoomControlComponent).toHaveLength(1)
      })

      it('should contain one button to zoom out', () => {
        // given
        props.hasExistingImage = false

        // when
        const wrapper = shallow(<UploadThumb {...props} />)

        const zoomControlComponent = wrapper
          .find('#zoomControl')
          .find('button')
          .at(0)

        // then
        expect(zoomControlComponent).toHaveLength(1)
        expect(zoomControlComponent.props().className).toStrictEqual('change-zoom decrement')
      })

      it('should contain one button to zoom in', () => {
        // given
        props.hasExistingImage = false

        // when
        const wrapper = shallow(<UploadThumb {...props} />)

        const zoomControlComponent = wrapper
          .find('#zoomControl')
          .find('button')
          .at(1)

        // then
        expect(zoomControlComponent).toHaveLength(1)
        expect(zoomControlComponent.props().className).toStrictEqual('change-zoom increment')
      })
    })
  })

  describe('handleDecrement', () => {
    it('should decrement zoom on click on minus button', () => {
      // given
      const getAttribute = jest.fn().mockImplementation(attribute => {
        if (attribute === 'step') {
          return 0.01
        }
        if (attribute === 'min') {
          return 1
        }
        if (attribute === 'max') {
          return 4
        }
      })

      // when
      const wrapper = shallow(<UploadThumb {...props} />)
      wrapper.instance()['handleSetZoomInput'] = {
        current: {
          getAttribute,
        },
      }
      wrapper.setState({ zoom: 1.1 })

      wrapper.find('.decrement').simulate('click')

      // then
      expect(wrapper.state('zoom')).toBe(1)
    })

    it('should increment zoom on click on plus button', () => {
      // given
      const getAttribute = jest.fn().mockImplementation(attribute => {
        if (attribute === 'step') {
          return 0.01
        }
        if (attribute === 'min') {
          return 1
        }
        if (attribute === 'max') {
          return 4
        }
      })

      // when
      const wrapper = shallow(<UploadThumb {...props} />)
      wrapper.instance()['handleSetZoomInput'] = {
        current: {
          getAttribute,
        },
      }

      wrapper.find('.increment').simulate('click')

      // then
      expect(wrapper.state('zoom')).toBe(1.1)
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
    const croppedRec = {
      height: 0.76,
      width: 0.45,
      x: 0.27,
      y: 0.11,
    }
    const getCroppingRect = jest.fn().mockImplementation(() => croppedRec)

    it('should not be called when no image', () => {
      // given
      props.image = null

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
      wrapper.instance()['avatarEditor'] = {
        current: {
          getCroppingRect,
        },
      }
      wrapper.instance().handleOnImageChange(ctx)

      // then
      expect(props.onImageChange).toHaveBeenCalledWith(ctx)
    })

    it('should be called with image, ctx and new coordonnates', () => {
      // given
      const wrapper = shallow(<UploadThumb {...props} />)

      // when
      wrapper.setState({ image, isUploadDisabled: false, size: 15038040 })
      wrapper.instance()['avatarEditor'] = {
        current: {
          getCroppingRect,
        },
      }
      const currentImage = wrapper.state('image')
      wrapper.instance().handleOnImageChange(ctx)

      // then
      expect(props.onImageChange).toHaveBeenCalledWith(ctx, currentImage, croppedRec)
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

  describe('isImageTooLarge', () => {
    it('should be false is image not larger than allowed', () => {
      // when
      const result = isImageTooLarge(2.5)

      // then
      expect(result).toStrictEqual(false)
    })

    it('should be true is image is larger than allowed', () => {
      // when
      const result = isImageTooLarge(12.5)

      // then
      expect(result).toStrictEqual(true)
    })
  })
})
