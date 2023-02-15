/**
 * @summary ValidationFilters help to toggle visibility of filters
 * @description hide/show validation filters and save state to localStorage
 *
 * @example
 * ```html
 * <div class="table-example">
 *   <button type="button" class="toggle-filters-button" disabled>Chargement...</button>
 *   <div class="filters">
 *      <!-- add your filters here -->
 *   </div>
 * </div>
 * <script>
 *   new PcValidationFilters({ $container: document.querySelector('.table-example'), localStorageKey: 'tableExample' })
 * </script>
 * ```
 */
class PcValidationFilters {
  static SHOW_LABEL = "Afficher les filtres"
  static HIDE_LABEL = "Masquer les filtres"
  $container
  localStorageKey

  constructor({ $container, localStorageKey }) {
    this.$container = $container
    this.localStorageKey = localStorageKey
    this.areUserOffererFiltersHidden = localStorage.getItem(localStorageKey) === "true"
    this.toggleSearchFilters(this.areUserOffererFiltersHidden)
    this.bindEvents()
  }

  get $toggleFiltersButton() {
    return this.$container.querySelector(".toggle-filters-button")
  }

  get $filters() {
    return this.$container.querySelector(".filters")
  }

  bindEvents = () => {
    this.$toggleFiltersButton.addEventListener(
      "click",
      () => {
        this.areUserOffererFiltersHidden = !this.areUserOffererFiltersHidden
        localStorage.setItem(this.localStorageKey, `${this.areUserOffererFiltersHidden}`)
        this.toggleSearchFilters(this.areUserOffererFiltersHidden)
      }
    )
  }

  toggleSearchFilters = (areFiltersHidden) => {
    this.$toggleFiltersButton.disabled = false
    this.$toggleFiltersButton.textContent = areFiltersHidden ? PcValidationFilters.SHOW_LABEL : PcValidationFilters.HIDE_LABEL
    this.$filters.classList[areFiltersHidden ? 'add' : 'remove']("d-none")
  }
}
