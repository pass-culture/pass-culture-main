
// createMachin
export default createSelectMachin = createSelector(
  state => state.data.machins,
  (state, ownProps) => ownProps.machinId,
  (machins, machinId) => machins && machins.find(machin =>
    machin.id === machinId)
)

// currentMachin (ou plutôt matchingMachin)
export default selectCurrentMachin = createSelectMachin()

// MachinPage
const MachinPage = ({
  machin
}) => {
  return (
    <div>
      {machin.name}
    </div>
  )
}
export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({
      machin: selectCurrentMachin(state, ownProps.match.params.machinId)
    })
  )
)(MachinPage)

BOUCLE REDUX A
selectCurrentMachin(state, ownProps) => cree un buffer => refiltre

BOUCLE REDUX B
selectCurrentMachin(state, ownProps) => compare ownPropsB, ownPropsA => retourne buffer si pas de chgmt






// MachinItem
const MachinItem = ({
  // CHOSE EST DONNE DU PARENT
  chose,
  machin
}) => {
  return (
    <div>
      {machin.name}
    </div>
  )
}


// NAIVE METHOD
export default connect(
  (state, ownProps) => createSelectMachin(state, ownProps.chose.machinId)
)(MachinItem)

BOUCLE REDUX A
item 1: createSelectMachin() => cree un buffer selectMachin => refiltre
item 2: utilise selectMachin => compare ownPropsA2 avec ownPropsA1 => refiltre

BOUCLE REDUX B
item 1: utilise selectMachin => compare ownPropsA1 avec ownPropsA2 => refiltre
item 2: utilise selectMachin => compare ownPropsB2 avec ownPropB1 => refiltre









// HEAVY METHOD
export default connect(
  (state, ownProps) => createSelectMachin()(state, ownProps.chose.machinId)
)(MachinItem)

BOUCLE REDUX A
item 1: createSelectMachin() => cree un buffer selectMachin => refiltre
item 2: createSelectMachin() => cree un buffer selectMachin => refiltre

BOUCLE REDUX B
item 1: createSelectMachin() => cree un buffer selectMachin => refiltre
item 2: createSelectMachin() => cree un buffer selectMachin => refiltre














// STACK METHOD
export default connect(
  () => {
    const selectMachin = createSelectMachin()
    return (state, ownProps) => selectMachin(state, ownProps.chose.machinId)
  }
)(MachinItem)

BOUCLE REDUX A
item 1: createSelectMachin() => cree un buffer selectMachin1 => refiltre
item 2: createSelectMachin() => cree un buffer selectMachin2 => refiltre

BOUCLE REDUX B
item 1: selectMachin1(state, ownProps) => compare ownPropsB1, ownPropsA1 => retourne buffer si pas de chgmt
item 2: selectMachin2(state, ownProps) => compare ownPropsB2, ownPropsA2 => retourne buffer si pas de chgmt
