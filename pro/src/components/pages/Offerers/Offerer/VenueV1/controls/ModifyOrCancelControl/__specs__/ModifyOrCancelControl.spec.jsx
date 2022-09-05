import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React, { Fragment } from 'react'
import { Field, Form } from 'react-final-form'

import ModifyOrCancelControl from '../ModifyOrCancelControl'

const history = {
  push: jest.fn(),
}

describe('src | components | pages | Venue | controls | ModifyOrCancelControl', () => {
  it('should redirect to homepage with offerer selected', async () => {
    // given
    const props = {
      isCreatedEntity: true,
      offererId: 'AE',
      readOnly: false,
    }

    render(
      <Form
        onSubmit={() => jest.fn()}
        render={({ form, handleSubmit }) => (
          <Fragment>
            <Field
              name="foo"
              render={({ input }) => <input name="foo" {...input} />}
            />
            <ModifyOrCancelControl
              form={form}
              handleSubmit={handleSubmit}
              history={history}
              {...props}
            />
          </Fragment>
        )}
      />
    )

    await userEvent.type(screen.getByRole('textbox'), 'bar')

    // when
    await userEvent.click(screen.getByRole('button'))

    // then
    const expectedPush = `/accueil?structure=${props.offererId}`
    expect(screen.getByRole('textbox')).toHaveValue('')
    expect(history.push).toHaveBeenCalledWith(expectedPush)
  })

  it('should redirect to venue page and reset form when click on cancel modified form', async () => {
    // given
    const props = {
      isCreatedEntity: false,
      offererId: 'AE',
      readOnly: false,
      venueId: 'AE',
    }

    render(
      <Form
        onSubmit={() => jest.fn()}
        render={({ form, handleSubmit }) => (
          <Fragment>
            <Field
              name="foo"
              render={({ input }) => <input name="foo" {...input} />}
            />
            <ModifyOrCancelControl
              form={form}
              handleSubmit={handleSubmit}
              history={history}
              {...props}
            />
          </Fragment>
        )}
      />
    )

    // when
    await userEvent.type(screen.getByRole('textbox'), 'bar')

    // then
    await userEvent.click(screen.getByRole('button'))

    // then
    const expectedPush = `/structures/${props.offererId}/lieux/${props.venueId}`
    expect(screen.getByRole('textbox')).toHaveValue('')
    expect(history.push).toHaveBeenCalledWith(expectedPush)
  })
})
