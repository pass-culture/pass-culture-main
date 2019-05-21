import { mount, shallow } from 'enzyme'
import React, { Fragment } from 'react'
import { Field, Form } from 'react-final-form'

import SubmitAndCancelControl from '../SubmitAndCancelControl'

describe('src | components | pages | Offer | StocksManagerContainer | StockItem | SubmitAndCancelControl ', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<SubmitAndCancelControl {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('mount', () => {
    it('should redirect and reset form when click on cancel', done => {
      // given
      const query = {
        changeToReadOnly: jest.fn(),
      }
      const stockId = 'AE'
      const wrapper = mount(
        <Form
          onSubmit={() => jest.fn()}
          render={({ form, handleSubmit }) => (
            <Fragment>
              <Field
                name="foo"
                render={({ input }) => <input name="foo" {...input} />}
              />
              <SubmitAndCancelControl
                form={form}
                handleSubmit={handleSubmit}
                isRequestPending={false}
                query={query}
                stockId={stockId}
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
        expect(wrapper.find("input[name='foo']").props().value).toEqual('bar')

        // when
        const cancelButton = wrapper.find('button.cancel-step')
        cancelButton.simulate('click')

        // then
        expect(wrapper.find("input[name='foo']").props().value).toEqual('')
        expect(query.changeToReadOnly).toHaveBeenCalledWith(null, {
          id: stockId,
          key: 'stock',
        })

        // done
        done()
      })
    })
  })
})
