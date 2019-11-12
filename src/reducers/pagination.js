const UPDATE_PAGE = 'UPDATE_PAGE'

const initialState = {
  page: 1,
  seed: Math.random()
}

const pagination = (state = initialState, action) => {
  if (action.type === UPDATE_PAGE) {
    return Object.assign({}, state, { page: action.page })
  } else {
    return state
  }
}

export const updatePage = (page) => ({
  page,
  type: UPDATE_PAGE,
})

export default pagination
