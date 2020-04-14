import React from 'react'
import { mount } from 'enzyme'
import RibUploadFeatureFlip from '../RibUpload'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'

const Children = () => 'child_component'
const Legacy = () => 'legacy_component'

describe('src | components | pages | Offerer', () => {
  const mockStore = configureStore()
  let props
  beforeEach(() => {
    props = {
      children: <Children />,
      legacy: <Legacy />,
    }
  })

  describe('render', () => {
    it('should render legacy component by default', () => {
      // given
      const store = mockStore({
        data: {
          features: [],
        },
      })

      // when
      const wrapper = mount(
        <Provider store={store}>
          <RibUploadFeatureFlip {...props} />
        </Provider>
      )

      // then
      const leg = wrapper.find(Legacy)
      expect(leg).toHaveLength(1)

      const child = wrapper.find(Children)
      expect(child).toHaveLength(0)
    })

    it('should render legacy component when feature flip is false in the store', () => {
      // given
      const store = mockStore({
        data: {
          features: [{ nameKey: 'NEW_RIBS_UPLOAD', isActive: false }],
        },
      })

      // when
      const wrapper = mount(
        <Provider store={store}>
          <RibUploadFeatureFlip {...props} />
        </Provider>
      )

      // then
      const leg = wrapper.find(Legacy)
      expect(leg).toHaveLength(1)

      const child = wrapper.find(Children)
      expect(child).toHaveLength(0)
    })

    it('should render children component when feature flip is activated', () => {
      // given
      const store = mockStore({
        data: {
          features: [{ nameKey: 'NEW_RIBS_UPLOAD', isActive: true }],
        },
      })

      // when
      const wrapper = mount(
        <Provider store={store}>
          <RibUploadFeatureFlip {...props} />
        </Provider>
      )

      // then
      const child = wrapper.find(Children)
      expect(child).toHaveLength(1)

      const leg = wrapper.find(Legacy)
      expect(leg).toHaveLength(0)
    })
  })
})
