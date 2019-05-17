import { mount } from 'enzyme'
import 'moment-timezone'
import React from 'react'
import { Field, Form } from 'react-final-form'
import adaptBookingLimitDateTimeGivenBeginningDateTime from '../adaptBookingLimitDateTimeGivenBeginningDateTime'

describe('src | components | pages | Offer | StockManager | StockItem | decorators | adaptBookingLimitDateTimeGivenBeginningDateTime', () => {
  describe('For event', () => {
    describe('bookingLimitDateTime updated', () => {
      test('Booking limit time equal to 23h59 if booking limit date is before beginning date', () => {
        // given
        const initialValues = {
          fooBeginningDate: '2019-04-28T19:00:00.000Z',
          fooBookingDate: '2019-04-28T19:00:00.000Z',
        }

        // when
        const wrapper = mount(
          <Form
            decorators={[
              adaptBookingLimitDateTimeGivenBeginningDateTime({
                isEvent: true,
              }),
            ]}
            initialValues={initialValues}
            onSubmit={onSubmit}
            render={({ handleSubmit }) => (
              <form>
                <Field
                  name="fooBeginningDate"
                  render={({ input }) => <input {...input} />}
                />
                <Field
                  name="fooBookingDate"
                  render={({ input }) => <input {...input} />}
                />
                <button onClick={handleSubmit} type="submit">
                  Submit
                </button>
              </form>
            )}
          />
        )

        // then
        setTimeout(() => {
          wrapper.update()
          const fooBookingDate = wrapper
            .find(Field)
            .find({ name: 'fooBookingDate' })
            .find('input')
          expect(fooBookingDate.props().value).toEqual(
            '2019-04-28T19:00:00.000Z'
          )

          // when
          fooBookingDate.simulate('change', {
            target: { value: '2019-04-27T19:00:00.000Z' },
          })
          setTimeout(() => {
            wrapper.update()
            wrapper.find('button[type="submit"]').simulate('click')
          })
        })

        // then
        function onSubmit(formValues) {
          expect(formValues.fooBookingDate).toEqual('2019-04-27T23:59:00.000Z')
        }
      })

      test('Booking limit time equal to beginning time if booking limit date is equal to beginning date', () => {
        // given
        const initialValues = {
          fooBeginningDate: '2019-04-28T19:00:00.000Z',
          fooBookingDate: '2019-04-20T23:59:00.000Z',
        }

        // when
        const wrapper = mount(
          <Form
            decorators={[
              adaptBookingLimitDateTimeGivenBeginningDateTime({
                isEvent: true,
              }),
            ]}
            initialValues={initialValues}
            onSubmit={onSubmit}
            render={({ handleSubmit }) => (
              <form>
                <Field
                  name="fooBeginningDate"
                  render={({ input }) => <input {...input} />}
                />
                <Field
                  name="fooBookingDate"
                  render={({ input }) => <input {...input} />}
                />
                <button onClick={handleSubmit} type="submit">
                  Submit
                </button>
              </form>
            )}
          />
        )

        // then
        setTimeout(() => {
          wrapper.update()
          const fooBookingDate = wrapper
            .find(Field)
            .find({ name: 'fooBookingDate' })
            .find('input')
          expect(fooBookingDate.props().value).toEqual(
            '2019-04-20T23:59:00.000Z'
          )

          // when
          fooBookingDate.simulate('change', {
            target: { value: '2019-04-28T23:59:00.000Z' },
          })
          setTimeout(() => {
            wrapper.update()
            wrapper.find('button[type="submit"]').simulate('click')
          })
        })

        // then
        function onSubmit(formValues) {
          expect(formValues.fooBookingDate).toEqual('2019-04-28T19:00:00.000Z')
        }
      })
    })

    describe('beginningDateTime updated', () => {
      test('Booking limit time equal to 23h59 if booking limit date is before beginning date', () => {
        // given
        const initialValues = {
          fooBeginningDate: '2019-04-28T19:00:00.000Z',
          fooBookingDate: '2019-04-28T19:00:00.000Z',
        }

        // when
        const wrapper = mount(
          <Form
            decorators={[
              adaptBookingLimitDateTimeGivenBeginningDateTime({
                isEvent: true,
              }),
            ]}
            initialValues={initialValues}
            onSubmit={onSubmit}
            render={({ handleSubmit }) => (
              <form>
                <Field
                  name="fooBeginningDate"
                  render={({ input }) => <input {...input} />}
                />
                <Field
                  name="fooBookingDate"
                  render={({ input }) => <input {...input} />}
                />
                <button onClick={handleSubmit} type="submit">
                  Submit
                </button>
              </form>
            )}
          />
        )

        // then
        setTimeout(() => {
          wrapper.update()
          const fooBeginningDate = wrapper
            .find(Field)
            .find({ name: 'fooBeginningDate' })
            .find('input')
          expect(fooBeginningDate.props().value).toEqual(
            '2019-04-28T19:00:00.000Z'
          )

          // when
          fooBeginningDate.simulate('change', {
            target: { value: '2019-04-29T19:00:00.000Z' },
          })
          setTimeout(() => {
            wrapper.update()
            wrapper.find('button[type="submit"]').simulate('click')
          })
        })

        // then
        function onSubmit(formValues) {
          expect(formValues.fooBookingDate).toEqual('2019-04-28T23:59:00.000Z')
        }
      })

      test('Booking limit time equal to beginning time if booking limit date is equal to beginning date', () => {
        // given
        const initialValues = {
          fooBeginningDate: '2019-04-28T19:00:00.000Z',
          fooBookingDate: '2019-04-20T23:59:00.000Z',
        }

        // when
        const wrapper = mount(
          <Form
            decorators={[
              adaptBookingLimitDateTimeGivenBeginningDateTime({
                isEvent: true,
              }),
            ]}
            initialValues={initialValues}
            onSubmit={onSubmit}
            render={({ handleSubmit }) => (
              <form>
                <Field
                  name="fooBeginningDate"
                  render={({ input }) => <input {...input} />}
                />
                <Field
                  name="fooBookingDate"
                  render={({ input }) => <input {...input} />}
                />
                <button onClick={handleSubmit} type="submit">
                  Submit
                </button>
              </form>
            )}
          />
        )

        // then
        setTimeout(() => {
          wrapper.update()
          const fooBeginningDate = wrapper
            .find(Field)
            .find({ name: 'fooBeginningDate' })
            .find('input')
          expect(fooBeginningDate.props().value).toEqual(
            '2019-04-28T19:00:00.000Z'
          )

          // when
          fooBeginningDate.simulate('change', {
            target: { value: '2019-04-20T19:00:00.000Z' },
          })
          setTimeout(() => {
            wrapper.update()
            wrapper.find('button[type="submit"]').simulate('click')
          })
        })

        // then
        function onSubmit(formValues) {
          expect(formValues.fooBookingDate).toEqual('2019-04-28T19:00:00.000Z')
        }
      })
    })
  })

  describe('For thing', () => {
    test('Booking limit time equal to 23h59 when booking limit date is not empty', () => {
      // given
      const initialValues = {
        fooBookingDate: null,
      }

      // when
      const wrapper = mount(
        <Form
          decorators={[
            adaptBookingLimitDateTimeGivenBeginningDateTime({
              isEvent: false,
              timezone: 'America/Cayenne',
            }),
          ]}
          initialValues={initialValues}
          onSubmit={onSubmit}
          render={({ handleSubmit }) => (
            <form>
              <Field
                name="fooBookingDate"
                render={({ input }) => <input {...input} />}
              />
              <button onClick={handleSubmit} type="submit">
                Submit
              </button>
            </form>
          )}
        />
      )

      // then
      setTimeout(() => {
        wrapper.update()
        const fooBookingDate = wrapper
          .find(Field)
          .find({ name: 'fooBookingDate' })
          .find('input')
        expect(fooBookingDate.props().value).toBeNull()

        // when
        fooBookingDate.simulate('change', {
          target: { value: '2019-04-27T19:00:00.000Z' },
        })
        setTimeout(() => {
          wrapper.update()
          wrapper.find('button[type="submit"]').simulate('click')
        })
      })

      // then
      function onSubmit(formValues) {
        expect(formValues.fooBookingDate).toEqual('2019-04-27T23:59:00.000Z')
      }
    })
  })
})
