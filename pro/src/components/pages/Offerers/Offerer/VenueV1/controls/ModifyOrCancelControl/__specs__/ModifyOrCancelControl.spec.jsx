import { mount } from 'enzyme'
import React, { Fragment } from 'react'
import { Field, Form } from 'react-final-form'

import ModifyOrCancelControl from '../ModifyOrCancelControl'

const history = {
  push: jest.fn(),
}

describe('src | components | pages | Venue | controls | ModifyOrCancelControl', () => {
  it('should redirect to homepage with offerer selected', async () => {
    await new Promise(done => {
      // given
      const props = {
        isCreatedEntity: true,
        offererId: 'AE',
        readOnly: false,
      }

      const wrapper = mount(
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
      wrapper
        .find("input[name='foo']")
        .simulate('change', { target: { value: 'bar' } })

      // when
      setTimeout(() => {
        // then
        wrapper.update()
        expect(wrapper.find("input[name='foo']").props().value).toBe('bar')

        // when
        const cancelButton = wrapper.find('button[type="reset"]')
        cancelButton.simulate('click')

        // then
        const expectedPush = `/accueil?structure=${props.offererId}`
        expect(wrapper.find("input[name='foo']").props().value).toBe('')
        expect(history.push).toHaveBeenCalledWith(expectedPush)

        // done
        done()
      })
    })
  })

  it('should redirect to venue page and reset form when click on cancel modified form', () => {
    // given
    const props = {
      isCreatedEntity: false,
      offererId: 'AE',
      readOnly: false,
      venueId: 'AE',
    }

    const wrapper = mount(
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
    wrapper
      .find("input[name='foo']")
      .simulate('change', { target: { value: 'bar' } })

    // then
    expect(wrapper.find("input[name='foo']").props().value).toBe('bar')

    // when
    const cancelButton = wrapper.find('button[type="reset"]')
    cancelButton.simulate('click')

    // then
    const expectedPush = `/structures/${props.offererId}/lieux/${props.venueId}`
    expect(wrapper.find("input[name='foo']").props().value).toBe('')
    expect(history.push).toHaveBeenCalledWith(expectedPush)
  })
})
