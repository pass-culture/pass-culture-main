/**
 * Addon to add filters toggling using a button and make their state persistent.
 *
 * @example
 * <div class="table-example" data-toggle="filters" data-toggle-id="something-unique">
 *   <button type="button" class="filters-toggle-button" disabled>Chargement...</button>
 *   <div class="filters-container">
 *      <!-- add your filters here -->
 *   </div>
 * </div>
 */
class PcValidationFilters extends PcAddOn {
  static FILTER_SELECTOR = '[data-toggle="filters"]'
  static TOGGLE_FILTERS_BUTTON_SELECTOR = '.filters-toggle-button'
  static FILTERS_CONTAINER_SELECTOR = '.filters-container'

  static SHOW_LABEL = "Afficher les filtres"
  static HIDE_LABEL = "Masquer les filtres"
  static IS_INITIAL_HIDDEN = false

  get $filters() {
    return document.querySelectorAll(PcValidationFilters.FILTER_SELECTOR)
  }

  initialize = () => {
    this.$filters.forEach(($filter) => {
      const { toggleId } = $filter.dataset
      this.state[toggleId] = this.state[toggleId] || PcValidationFilters.IS_INITIAL_HIDDEN
      this.#toggleFiltersContainer($filter, this.state[toggleId])
    })
  }

  bindEvents = () => {
    this.$filters.forEach(($filter) => {
      EventHandler.on($filter, 'click', PcValidationFilters.TOGGLE_FILTERS_BUTTON_SELECTOR, this.#onToggleFilterButtonClick)
    })
  }

  unbindEvents = () => {
    this.$filters.forEach(($filter) => {
      EventHandler.off($filter, 'click', PcValidationFilters.TOGGLE_FILTERS_BUTTON_SELECTOR, this.#onToggleFilterButtonClick)
    })
  }

  #getToggleFiltersButton = ($filter) => {
    return $filter.querySelector(PcValidationFilters.TOGGLE_FILTERS_BUTTON_SELECTOR)
  }

  #getFiltersContainer = ($filter) => {
    return $filter.querySelector(PcValidationFilters.FILTERS_CONTAINER_SELECTOR)
  }

  #onToggleFilterButtonClick = (event) => {
    const { toggleId } = event.currentTarget.dataset
    this.state[toggleId] = !this.state[toggleId]
    this.saveState(this.state)
    this.#toggleFiltersContainer(event.currentTarget, this.state[toggleId])
  }

  #toggleFiltersContainer = ($filter, isHidden) => {
    this.#getToggleFiltersButton($filter).disabled = false
    this.#getToggleFiltersButton($filter).textContent = isHidden ? PcValidationFilters.SHOW_LABEL : PcValidationFilters.HIDE_LABEL
    this.#getFiltersContainer($filter).classList[isHidden ? 'add' : 'remove']('d-none')
  }
}
