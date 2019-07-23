import CsvTableButton from '../CsvTableButton'
import { shallow } from 'enzyme'
import React from 'react'

describe('src | components | layout | CsvTableButton', () => {
  let props

  beforeEach(() => {
    props = {
      children: 'foobar',
      downloadFileOrNotifyAnError: jest.fn(),
      history: {
        push: jest.fn(),
      },
      location: {
        pathname: '/fake-url',
      },
      showFailureNotification: jest.fn(),
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<CsvTableButton {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a CsvTableButton component with the default state', () => {
      // when
      const wrapper = shallow(<CsvTableButton {...props} />)

      // then
      expect(wrapper.state()).toStrictEqual({ isLoading: false })
    })

    it('should render a button with the default props', () => {
      // when
      const wrapper = shallow(<CsvTableButton {...props} />)

      // then
      expect(wrapper.prop('className')).toBe('button is-primary')
      expect(wrapper.prop('onClick')).toStrictEqual(expect.any(Function))
      expect(wrapper.prop('type')).toBe('button')
      expect(wrapper.text()).toBe('foobar')
    })

    it('should render a button with the right css classes when state isLoading value is true', () => {
      // when
      const wrapper = shallow(<CsvTableButton {...props} />)
      wrapper.setState({ isLoading: true })

      // then
      expect(wrapper.prop('className')).toBe('button is-primary is-loading')
    })
  })

  describe('handleRequestData', () => {
    it('should redirect to next url when data fetching is successful', async () => {
      // given
      props.downloadFileOrNotifyAnError.mockReturnValue({
        data: [['data1', 'data2']],
        headers: ['column1', 'column2'],
      })
      const wrapper = shallow(<CsvTableButton {...props} />)

      // when
      await wrapper.instance().handleRequestData()

      // then
      expect(props.history.push).toHaveBeenCalledWith('/fake-url/detail', {
        data: [['data1', 'data2']],
        headers: ['column1', 'column2'],
      })
    })

    it('should display a failure notification when no data were fetched', async () => {
      // given
      props.downloadFileOrNotifyAnError.mockReturnValue({
        data: [],
        headers: ['column1', 'column2'],
      })
      const wrapper = shallow(<CsvTableButton {...props} />)

      // when
      await wrapper.instance().handleRequestData()

      // then
      expect(props.showFailureNotification).toHaveBeenCalledWith()
    })

    it('should set isLoading value from state to false when fetching is finished', async () => {
      // given
      props.downloadFileOrNotifyAnError.mockReturnValue({
        data: [],
        headers: ['column1', 'column2'],
      })
      const wrapper = shallow(<CsvTableButton {...props} />)

      // when
      await wrapper.instance().handleRequestData()

      // then
      expect(wrapper.state('isLoading')).toBe(false)
    })
  })
})
