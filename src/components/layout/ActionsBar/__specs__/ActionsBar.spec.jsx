import '@testing-library/jest-dom'
import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import configureStore from 'store'
import { initialState, showActionsBar } from 'store/reducers/actionsBar'
import { renderWithStyles } from 'utils/testHelpers'

import ActionsBar from '../'

const renderActionsBar = (props, store) => {
  return renderWithStyles(
    <Provider store={store}>
      <ActionsBar {...props}>
        <div>
          {'actionsBar content'}
        </div>
      </ActionsBar>
    </Provider>,
    {
      stylesheet: 'global/_ActionsBar.scss',
    }
  )
}

describe('src | components | layout | ActionsBar', () => {
  let store
  let props
  beforeEach(() => {
    store = configureStore({ actionsBar: initialState }).store
    props = {}
  })

  it('should not be visible by default', () => {
    renderActionsBar(props, store)
    expect(screen.getByText('actionsBar content')).not.toBeVisible()
  })

  it('should be visible on store.ActionsBar.actionsBarVisibility update', async () => {
    renderActionsBar(props, store)

    store.dispatch(showActionsBar())

    await waitFor(() => expect(screen.getByText('actionsBar content')).toBeVisible())
  })
})
