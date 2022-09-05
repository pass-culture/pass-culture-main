import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'

import ReturnOrSubmitControl from '../ReturnOrSubmitControl'

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
  const renderReturnOrSubmitControl = props => {
    const store = configureTestStore()
    return render(
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
    renderReturnOrSubmitControl(props)

    // then
    expect(screen.getByRole('link')).toHaveAttribute(
      'href',
      '/accueil?structure=ABC'
    )
  })

  it('should display a button with the right props when not read-only mode, is not request pending, can submit, and is in creation mode', () => {
    // given
    props.readOnly = false
    props.isRequestPending = false

    // when
    renderReturnOrSubmitControl(props)
    // then

    const button = screen.getByRole('button')

    expect(button).toHaveAttribute('type', 'submit')
    expect(button).toHaveTextContent('Créer')
  })

  it('should display a button with the right props when not read-only mode, is request pending, can not submit, and is not in creation mode', () => {
    // given
    props.canSubmit = false
    props.readOnly = false
    props.isCreatedEntity = false
    props.isRequestPending = true

    // when
    renderReturnOrSubmitControl(props)

    // then
    const button = screen.getByRole('button')

    expect(button).toHaveAttribute('disabled')
    expect(button).toHaveAttribute('type', 'submit')
    expect(button).toHaveTextContent('Valider')
  })
})
