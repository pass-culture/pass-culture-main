function doesTokenHaveBeenChecked(state) {
  const {
    token: { hasBeenChecked },
  } = state

  return hasBeenChecked
}

export default doesTokenHaveBeenChecked
