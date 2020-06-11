import { mount, shallow } from 'enzyme'
import React, { Fragment } from 'react'
import { Field, Form } from 'react-final-form'

import SubmitAndCancelControl from '../SubmitAndCancelControl'

describe('src | components | pages | Offer | StocksManagerContainer | StockItem | SubmitAndCancelControl ', () => {
  it('should match the snapshot', () => {
    // given
    const initialProps = {
      form: {},
      handleSubmit: () => jest.fn(),
      isRequestPending: false,
      query: {},
    }

    // when
    const wrapper = shallow(<SubmitAndCancelControl {...initialProps} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('mount', () => {
    it('should redirect and reset form when click on cancel', () => {
      // given
      const query = {
        changeToReadOnly: jest.fn(),
      }
      const stockId = 'AE'

      const onSubmitMock = () => jest.fn()
      const renderField = ({ input }) => (<input
        name="foo"
        {...input}
                                          />)

      const renderForm = ({ form, handleSubmit }) => (
        <Fragment>
          <Field
            name="foo"
            render={renderField}
          />
          <table>
            <tbody>
              <tr>
                <SubmitAndCancelControl
                  form={form}
                  handleSubmit={handleSubmit}
                  isRequestPending={false}
                  query={query}
                  stockId={stockId}
                />
              </tr>
            </tbody>
          </table>
        </Fragment>
      )
      const wrapper = mount(
        <Form
          onSubmit={onSubmitMock}
          render={renderForm}
        />
      )

      // when
      wrapper.find("input[name='foo']").simulate('change', { target: { value: 'bar' } })

      // when
      expect(wrapper.find("input[name='foo']").props().value).toStrictEqual('bar')

      // when
      const cancelButton = wrapper.find('button.cancel-step')
      cancelButton.simulate('click')

      // then
      expect(wrapper.find("input[name='foo']").props().value).toStrictEqual('')
      expect(query.changeToReadOnly).toHaveBeenCalledWith(null, {
        id: stockId,
        key: 'stock',
      })
    })
  })
})
