/**
 * Adds client-side pagination, search, and filtering capabilities to an HTML table.
 * The addon automatically scans the table rows, generates pagination controls, and
 * handles row visibility based on the current page and active search criteria.
 *
 * It is configured using data attributes on the table and its cells.
 *
 * ---
 *
 * ### HTML Configuration
 *
 * - **`.pc-table-paginator`**: The required class to activate the addon on a `<table>`.
 * - **`id`**: The table must have a unique `id`.
 *
 * ### Data Attributes for `<table>`
 *
 * - `data-pc-items-per-page`: (Optional) Number of rows to display per page. **Default: `20`**.
 * - `data-pc-max-visible-pages`: (Optional) The maximum number of page links to display in the pagination control. **Default: `20`**.
 * - `data-pc-show-total-count`: (Optional) If set to `"true"`, displays a "X résultats" count above the table.
 * - `data-pc-search-container-id`: (Optional) The `id` of an element that contains search controls (`input[type="text"]` and `select`).
 *
 * ### Data Attributes for `<td>`
 *
 * - `data-search-key`: To make a column searchable, add this attribute to its `<td>` elements.
 *                    The value must match an `<option>` value in the filter `select`.
 *
 * ---
 *
 * @example
 * <div id="linked-offer-search-controls">
 *   <input type="text"
 *          class="form-control"
 *          id="search-linked-offers"
 *          placeholder="Rechercher dans les offres liées..." />
 *   <select class="form-select form-control value-element-form" id="filter-select-linked-offer">
 *     <option value="all">Filtrer sur tous les champs</option>
 *     <option value="id">ID</option>
 *     <option value="name">Nom</option>
 *     <option value="venue">Partenaire culturel</option>
 *     <option value="status">Statut</option>
 *     <option value="dateCreated">Date de création</option>
 *   </select>
 * </div>
 *
 * <table id="offers-table"
 *        class="table table-borderless table-hover pc-table-paginator d-none"
 *        data-pc-items-per-page="20"
 *        data-pc-max-visible-pages="20"
 *        data-pc-show-total-count="true"
 *        data-pc-search-container-id="linked-offer-search-controls">
 *   <thead class="table-light">
 *     <tr>
 *       <th>ID</th>
 *       <th>Nom</th>
 *       <th>Partenaire culturel</th>
 *       <th>Statut</th>
 *       <th>Date de création</th>
 *     </tr>
 *   </thead>
 *   <tbody>
 *     <tr>
 *       <td data-search-key="id">1</td>
 *       <td data-search-key="name">Offre 1</td>
 *       <td data-search-key="venue">Partenaire culturel</td>
 *       <td data-search-key="status">Épuisée</td>
 *       <td data-search-key="dateCreated">2025/06/12</td>
 *     </tr>
 *   </tbody>
 * </table>
 */
class PcTablePaginator extends PcAddOn {
  static SELECTOR = '.pc-table-paginator'
  static CONTROLS_CONTAINER = 'pc-paginator-controls'
  static PREVIOUS_BUTTON = 'pc-paginator-prev'
  static NEXT_BUTTON = 'pc-paginator-next'
  static PAGE_LINK = 'pc-paginator-page'
  static SEARCH_INPUT_SELECTOR = 'input[type="text"]'
  static SEARCH_SELECT_SELECTOR = 'select'
  static DEFAULT_ITEMS_PER_PAGE = 20
  static DEFAULT_MAX_VISIBLE_PAGES = 20

  get $tables() {
    return document.querySelectorAll(PcTablePaginator.SELECTOR)
  }

  #paginators = {}

  #initializePaginatorForTable = ($table) => {
    const tableId = $table.id

    const $trElements = Array.from($table.querySelectorAll('tbody tr'))
    if ($trElements.length === 0) {
      $table.classList.remove('d-none')
      return;
    }

    const allRows = $trElements.map($tr => {
      const searchableColumns = {};
      $tr.querySelectorAll('td[data-search-key]').forEach($cell => {
        const key = $cell.dataset.searchKey;
        const value = $cell.textContent;
        searchableColumns[key] = value.toLowerCase();
      });
      return {
        $element: $tr,
        searchableColumns: searchableColumns
      };
    });

    const showTotalCount = $table.dataset.pcShowTotalCount === 'true'
    const itemsPerPage = parseInt($table.dataset.pcItemsPerPage, 10) || PcTablePaginator.DEFAULT_ITEMS_PER_PAGE
    const maxVisiblePages = parseInt($table.dataset.pcMaxVisiblePages, 10) || PcTablePaginator.DEFAULT_MAX_VISIBLE_PAGES

    let $paginationControlsContainer = document.createElement('div')
    $paginationControlsContainer.classList.add(PcTablePaginator.CONTROLS_CONTAINER)
    $table.after($paginationControlsContainer)

    this.#paginators[tableId] = {
      $table: $table,
      allRows: allRows,
      $filteredRows: allRows,
      $paginationControlsContainer: $paginationControlsContainer,
      totalItems: allRows.length,
      showTotalCount: showTotalCount,
      itemsPerPage: itemsPerPage,
      totalPages: Math.ceil(allRows.length / itemsPerPage),
      maxVisiblePages: maxVisiblePages,
      currentPage: 1,
      searchContainerId: $table.dataset.pcSearchContainerId || null,
      $searchInput: null,
      $searchSelect: null,
      searchQuery: '',
      searchColumn: 'all',
      searchHandler: null,
      filterChangeHandler: null
    }

    this.#initializeSearch(tableId)
    this.#updateUI(tableId)
  }

  #initializeSearch = (tableId) => {
    const state = this.#paginators[tableId]
    if (!state.searchContainerId) {
      return;
    }

    const $searchContainer = document.getElementById(state.searchContainerId)
    if (!$searchContainer) {
      return;
    }

    state.$searchInput = $searchContainer.querySelector(PcTablePaginator.SEARCH_INPUT_SELECTOR)
    state.$searchSelect = $searchContainer.querySelector(PcTablePaginator.SEARCH_SELECT_SELECTOR)

    if (state.$searchInput) {
      state.searchHandler = () => this.#onSearchOrFilterChange(tableId)
    }

    if (state.$searchSelect) {
      state.filterChangeHandler = () => this.#onSearchOrFilterChange(tableId)
    }
  }

  #updateUI = (tableId) => {
    this.#updateTopControls(tableId)
    this.#updatePaginationControls(tableId)
    this.#renderPage(tableId)
  }

  #updateTopControls = (tableId) => {
    const $oldControls = document.querySelector(`[data-pc-paginator-top-controls-for="${tableId}"]`)
    if ($oldControls) {
      $oldControls.remove()
    }

    const state = this.#paginators[tableId]
    if (!state || !state.showTotalCount) {
      return;
    }

    const { $table, totalItems } = state
    const $topWrapper = document.createElement('div')
    $topWrapper.dataset.pcPaginatorTopControlsFor = tableId
    $topWrapper.className = 'mb-2'

    $topWrapper.innerHTML = `<p class="lead num-results-unlinked-offer">${totalItems} résultat${totalItems > 1 ? 's' : ''}</p>`

    $table.parentNode.insertBefore($topWrapper, $table)
  }

  #updatePaginationControls = (tableId) => {
    const state = this.#paginators[tableId]
    state.$paginationControlsContainer.innerHTML = ''
    if (state.totalPages <= 1) {
      return;
    }

    const $list = document.createElement('ul')
    $list.className = 'pagination'

    $list.appendChild(this.#createNavButton(tableId, 'Précédent', state.currentPage === 1))

    let startPage, endPage;
    if (state.totalPages <= state.maxVisiblePages) {
      startPage = 1; endPage = state.totalPages
    } else {
      const sidePages = Math.floor((state.maxVisiblePages - 1) / 2)
      if (state.currentPage <= sidePages) {
        startPage = 1; endPage = state.maxVisiblePages
      } else if (state.currentPage + sidePages >= state.totalPages) {
        startPage = state.totalPages - state.maxVisiblePages + 1; endPage = state.totalPages
      } else {
        startPage = state.currentPage - sidePages; endPage = state.currentPage + sidePages
      }
    }
    for (let i = startPage; i <= endPage; i++) {
      $list.appendChild(this.#createPageLink(i, state.currentPage, tableId));
    }

    $list.appendChild(this.#createNavButton(tableId, 'Suivant', state.currentPage === state.totalPages))

    const $nav = document.createElement('nav')
    $nav.setAttribute('aria-label', 'Table navigation')
    $nav.appendChild($list)
    state.$paginationControlsContainer.appendChild($nav)
  }

  #renderPage = (tableId) => {
    const state = this.#paginators[tableId]
    const { $table, allRows, $filteredRows, currentPage, itemsPerPage } = state

    $table.classList.add('d-none')
    allRows.forEach(row => row.$element.classList.add('d-none'))

    const startIndex = (currentPage - 1) * itemsPerPage
    const rowsToShow = $filteredRows.slice(startIndex, startIndex + itemsPerPage)
    rowsToShow.forEach(row => row.$element.classList.remove('d-none'))
    $table.classList.remove('d-none')
  }

  #createPageLink = (pageNum, currentPage, tableId) => {
      const $li = document.createElement('li')
      const isActive = pageNum === currentPage
      $li.className = `page-item ${isActive ? 'active' : ''}`
      $li.innerHTML = `<a class="page-link ${PcTablePaginator.PAGE_LINK} ${isActive ? 'fw-bold' : ''}" href="#" data-pc-target-table-id="${tableId}" data-pc-page="${pageNum}">${pageNum}</a>`
      return $li
  }

  #createNavButton = (tableId, text, isDisabled) => {
    const $li = document.createElement('li')
    const className = text === 'Précédent' ? PcTablePaginator.PREVIOUS_BUTTON : PcTablePaginator.NEXT_BUTTON
    $li.className = `page-item ${isDisabled ? 'disabled' : ''}`
    $li.innerHTML = `<a class="page-link ${className}" href="#" data-pc-target-table-id="${tableId}">${text}</a>`
    return $li
  }

  #getStateFromEvent = (event) => {
    const $trigger = event.target.closest('[data-pc-target-table-id]')
    return $trigger ? this.#paginators[$trigger.dataset.pcTargetTableId] : null
  }

  #refreshStateAndUI = (tableId) => {
    const state = this.#paginators[tableId]

    state.totalItems = state.$filteredRows.length
    state.totalPages = Math.ceil(state.totalItems / state.itemsPerPage)
    state.currentPage = 1

    this.#updateUI(tableId)
  }

  #onSearchOrFilterChange = (tableId) => {
    const state = this.#paginators[tableId]
    if (!state) {
      return;
    }

    state.searchQuery = state.$searchInput ? state.$searchInput.value.toLowerCase() : ''
    state.searchColumn = state.$searchSelect ? state.$searchSelect.value : 'all'

    state.$filteredRows = state.allRows.filter(row => {
      if (state.searchQuery === '') {
        return true
      }
      if (state.searchColumn === 'all') {
        return Object.values(row.searchableColumns).some(value =>
          value.includes(state.searchQuery)
        );
      } else {
        const cell = row.searchableColumns[state.searchColumn]
        return cell ? cell.includes(state.searchQuery) : false
      }
    })

    this.#refreshStateAndUI(tableId)
  }

  #onPageClick = (event) => {
    event.preventDefault()
    const state = this.#getStateFromEvent(event)
    if (!state) {
      return;
    }

    const page = parseInt(event.target.dataset.pcPage, 10)
    if (page && page !== state.currentPage) {
      state.currentPage = page
      const tableId = state.$table.id
      this.#renderPage(tableId)
      this.#updatePaginationControls(tableId)
    }
  }

  #onPrevClick = (event) => {
    event.preventDefault()
    const state = this.#getStateFromEvent(event)
    if (state && state.currentPage > 1) {
      state.currentPage--
      const tableId = state.$table.id
      this.#renderPage(tableId)
      this.#updatePaginationControls(tableId)
    }
  }

  #onNextClick = (event) => {
    event.preventDefault()
    const state = this.#getStateFromEvent(event)
    if (state && state.currentPage < state.totalPages) {
      state.currentPage++
      const tableId = state.$table.id
      this.#renderPage(tableId)
      this.#updatePaginationControls(tableId)
    }
  }

  initialize = () => {
    this.#paginators = {}
    this.$tables.forEach(this.#initializePaginatorForTable)
  }

  bindEvents = () => {
    EventHandler.on(document.body, 'click', `.${PcTablePaginator.PAGE_LINK}`, this.#onPageClick)
    EventHandler.on(document.body, 'click', `.${PcTablePaginator.PREVIOUS_BUTTON}`, this.#onPrevClick)
    EventHandler.on(document.body, 'click', `.${PcTablePaginator.NEXT_BUTTON}`, this.#onNextClick)

    for (const tableId in this.#paginators) {
      const state = this.#paginators[tableId];

      if (state.$searchInput && state.searchHandler) {
        state.$searchInput.addEventListener('input', state.searchHandler);
      }

      if (state.$searchSelect && state.filterChangeHandler) {
        state.$searchSelect.addEventListener('change', state.filterChangeHandler);
      }
    }
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'click', `.${PcTablePaginator.PAGE_LINK}`, this.#onPageClick)
    EventHandler.off(document.body, 'click', `.${PcTablePaginator.PREVIOUS_BUTTON}`, this.#onPrevClick)
    EventHandler.off(document.body, 'click', `.${PcTablePaginator.NEXT_BUTTON}`, this.#onNextClick)

    for (const tableId in this.#paginators) {
      const state = this.#paginators[tableId];

      if (state.$searchInput && state.searchHandler) {
        state.$searchInput.removeEventListener('input', state.searchHandler);
      }

      if (state.$searchSelect && state.filterChangeHandler) {
        state.$searchSelect.removeEventListener('change', state.filterChangeHandler);
      }
    }
  }
}
