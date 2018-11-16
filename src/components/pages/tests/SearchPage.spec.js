import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'
// import { createStore } from 'redux';

import REDUX_STATE from '../../../mocks/reduxState'

import SearchPage from '../SearchPage'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | SearchPage', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = REDUX_STATE
      const store = mockStore(initialState)

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <SearchPage />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('mapStateToProps', () => {
    // we are not testing the reducer, so it's ok to have a do-nothing reducer
    // const reducer = state => state;
    // // just a mock
    //
    // // this is how i mock the dispatch method
    // // cf https://github.com/reduxjs/redux/issues/1534
    // // const store = {
    // //   ...createStore(reducer, REDUX_STATE),
    // //   dispatch,
    // // };
    // const store = {
    //   dispatch: () => {},
    //   getState: () => ({
    //     REDUX_STATE,
    //   }),
    //   subscribe: () => {},
    // };
    // const wrapper = shallow(
    //   <SearchPage store={store} />,
    // );
    //   it('should update props values', () => {
    //     // given
    //     const initialState = REDUX_STATE
    //     const dispatch = jest.fn();
    //     const store = mockStore(initialState)
    //
    //     // const wrapper = shallow(<SearchPage store={store} />)
    //
    //     // const component = wrapper.find(SearchPageContent)
    //
    //     // console.log('wrapper', wrapper.props().children())
    //     // const wrapper = shallow(<SearchPage dispatch={dispatch} store={store}  />).dive({ context: {store: mockStore()}});
    //      // const wrapper = shallow(<SearchPage />, { context: { store } }).get(0);
    //      const wrapper = shallow(<SearchPage store={store} />)
    //      console.log('RYRYTRTR', wrapper.find('Connect(SearchPageContent)').find('withRouter(Connect(_withLogin))'))
    //
    //      expect(wrapper.find('Connect(SearchPageContent)').find('withRouter(Connect(_withLogin))')).toHaveLength(1)
    //
    //     expect(wrapper.find('Connect(SearchPageContent)')).toHaveLength(1)
    //     console.log('YEYEYEYRZTZE', wrapper.props().children);
    //
    // const typeSublabels = wrapper.prop('typeSublabels');
    // expect(typeSublabels).toBe('YTRYTRTYRYT');
    // expect(wrapper).toBeTruthy();
    // expect(component.props()).toEqual('region');
    // wrapper.props().children().props.store.dispatch(REDUX_STATE)
    // FIXME
    // export mapStateToProps
    // problem with withRouter
    // search for SearchPageContent props .dive() inside wrapper doesn't work
    // put a spy on mapStateToProps
    // })
  })
})
