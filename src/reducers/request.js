export const REQUEST_GET_PRODUCTS = 'REQUEST_GET_PRODUCTS'
export const SUCCESS_GET_PRODUCTS = 'SUCCESS_GET_PRODUCTS'

const initialState = {
  products: null
}

const request = (state=initialState, action) => {
  switch (action.type) {
    case SUCCESS_GET_PRODUCTS:
      return Object.assign({}, state, { products: action.data })
    default:
      return state
  }
}

export const requestGetProducts = () => ({
  type: REQUEST_GET_PRODUCTS
})

export const successGetProducts = data => ({
  data,
  type: SUCCESS_GET_PRODUCTS
})

export default request
