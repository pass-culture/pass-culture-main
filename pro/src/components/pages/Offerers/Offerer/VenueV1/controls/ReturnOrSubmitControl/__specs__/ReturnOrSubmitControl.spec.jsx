import { Link } from 'react-router-dom'
import { MemoryRouter } from 'react-router'
import { Provider } from 'react-redux'
import React from 'react'
import ReturnOrSubmitControl from '../ReturnOrSubmitControl'
import { configureTestStore } from 'store/testUtils'
import { mount } from 'enzyme'

describe('src | components | pages | Venue | controls | ReturnOrSubmitControl', () => {
  let props
  beforeEach(() => {
    props = {
      canSubmit: true,
      isCreatedEntity: true,
      isRequestPending: true,
      offererId: 'ABC',
      readOnly: true,
    }
  })
  const mountReturnOrSubmitControl = props => {
    const store = configureTestStore({ app: { logEvent: jest.fn() } })
    return mount(
      <Provider store={store}>
        <MemoryRouter>
          <ReturnOrSubmitControl {...props} />
        </MemoryRouter>
      </Provider>
    )
  }
  it("should display a return link to offerer's page when read-only mode", () => {
    // given
    props.readOnly = true

    // when
    const wrapper = mountReturnOrSubmitControl(props)

    // then
    const navLink = wrapper.find(Link)
    expect(navLink).toHaveLength(1)
    expect(navLink.prop('to')).toBe('/accueil?structure=ABC')
  })

  it('should display a button with the right props when not read-only mode, is not request pending, can submit, and is in creation mode', () => {
    // given
    props.readOnly = false
    props.isRequestPending = false

    // when
    const wrapper = mountReturnOrSubmitControl(props)
    // then
    const button = wrapper.find('ReturnOrSubmitControl').find('button')
    expect(button.prop('disabled')).toBe(false)
    expect(button.prop('type')).toBe('submit')
    expect(button.text()).toBe('Créer')
  })

  it('should display a button with the right props when not read-only mode, is request pending, can not submit, and is not in creation mode', () => {
    // given
    props.canSubmit = false
    props.readOnly = false
    props.isCreatedEntity = false
    props.isRequestPending = true

    // when
    const wrapper = mountReturnOrSubmitControl(props)

    // then
    const button = wrapper.find('button')
    expect(button.prop('disabled')).toBe(true)
    expect(button.prop('type')).toBe('submit')
    expect(button.text()).toBe('Valider')
  })
})
