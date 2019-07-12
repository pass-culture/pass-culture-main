const mapStateToProps = state => {
  const name = state.user && state.user.publicName

  return {
    name,
    offerers: state.data.offerers,
  }
}

export default mapStateToProps
