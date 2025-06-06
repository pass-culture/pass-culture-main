/**
Manage tables to simulate pagination and handle search
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
  static SEARCH_DEBOUNCE_DELAY = 300

  get $tables() {
    return document.querySelectorAll(PcTablePaginator.SELECTOR)
  }

  #paginators = {}

  #initializePaginatorForTable = ($table) => {
    const tableId = $table.id

    const $allRows = Array.from($table.querySelectorAll('tbody tr'))
    if ($allRows.length === 0) {
      return;
    }

    const showTotalCount = $table.dataset.pcShowTotalCount === 'true'
    const itemsPerPage = parseInt($table.dataset.pcItemsPerPage, 10) || PcTablePaginator.DEFAULT_ITEMS_PER_PAGE
    const maxVisiblePages = parseInt($table.dataset.pcMaxVisiblePages, 10) || PcTablePaginator.DEFAULT_MAX_VISIBLE_PAGES

    let $paginationControlsContainer = document.createElement('div')
    $paginationControlsContainer.classList.add(PcTablePaginator.CONTROLS_CONTAINER)
    $table.after($paginationControlsContainer)

    this.#paginators[tableId] = {
      $table,
      $allRows,
      $filteredRows: $allRows,
      $paginationControlsContainer,
      totalItems: $allRows.length,
      showTotalCount,
      itemsPerPage,
      totalPages: Math.ceil($allRows.length / itemsPerPage),
      maxVisiblePages,
      currentPage: 1,
      searchContainerId: $table.dataset.pcSearchContainerId || null,
      $searchInput: null,
      $searchSelect: null,
      searchQuery: '',
      searchColumn: 'all'
    }

    this.#initializeSearch(tableId)
    this.#updateUI(tableId)
  }

  #debounce = (func, delay) => {
    let timeoutId
    return (...args) => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => func(...args), delay)
    }
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
      const debouncedSearch = this.#debounce(() => this.#onSearchOrFilterChange(tableId), PcTablePaginator.SEARCH_DEBOUNCE_DELAY)
      state.$searchInput.addEventListener('input', debouncedSearch)
    }

    if (state.$searchSelect) {
      state.$searchSelect.addEventListener('change', () => this.#onSearchOrFilterChange(tableId))
    }
  }

  #updateUI = (tableId) => {
    this.#updateTopControls(tableId)
    this.#updatePaginationControls(tableId)
    this.#renderPage(tableId)
  }

  #updateTopControls = (tableId) => {
    const oldControls = document.querySelector(`[data-pc-paginator-top-controls-for="${tableId}"]`)
    if (oldControls) {
      oldControls.remove()
    }

    const state = this.#paginators[tableId]
    if (!state || !state.showTotalCount) {
      return;
    }

    const { $table, totalItems } = state
    const topWrapper = document.createElement('div')
    topWrapper.dataset.pcPaginatorTopControlsFor = tableId
    topWrapper.className = 'mb-2'

    topWrapper.innerHTML = `<p class="lead num-results-unlinked-offer">${totalItems} résultat${totalItems > 1 ? 's' : ''}</p>`

    $table.parentNode.insertBefore(topWrapper, $table)
  }

  #updatePaginationControls = (tableId) => {
    const state = this.#paginators[tableId]
    state.$paginationControlsContainer.innerHTML = ''
    if (state.totalPages <= 1) {
      return;
    }

    const list = document.createElement('ul')
    list.className = 'pagination'

    list.appendChild(this.#createNavButton(tableId, 'Précédent', state.currentPage === 1))

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
      list.appendChild(this.#createPageLink(i, state.currentPage, tableId));
    }

    list.appendChild(this.#createNavButton(tableId, 'Suivant', state.currentPage === state.totalPages))

    const nav = document.createElement('nav')
    nav.setAttribute('aria-label', 'Table navigation')
    nav.appendChild(list)
    state.$paginationControlsContainer.appendChild(nav)
  }

  #renderPage = (tableId) => {
    const state = this.#paginators[tableId]
    const { $allRows, $filteredRows, currentPage, itemsPerPage } = state

    $allRows.forEach(row => row.classList.add('d-none'))

    const startIndex = (currentPage - 1) * itemsPerPage
    const rowsToShow = $filteredRows.slice(startIndex, startIndex + itemsPerPage)
    rowsToShow.forEach(row => row.classList.remove('d-none'))
  }

  #createPageLink = (pageNum, currentPage, tableId) => {
      const li = document.createElement('li')
      const isActive = pageNum === currentPage
      li.className = `page-item ${isActive ? 'active' : ''}`
      li.innerHTML = `<a class="page-link ${PcTablePaginator.PAGE_LINK} ${isActive ? 'fw-bold' : ''}" href="#" data-pc-target-table-id="${tableId}" data-pc-page="${pageNum}">${pageNum}</a>`
      return li
  }

  #createNavButton = (tableId, text, isDisabled) => {
    const li = document.createElement('li')
    const className = text === 'Précédent' ? PcTablePaginator.PREVIOUS_BUTTON : PcTablePaginator.NEXT_BUTTON
    li.className = `page-item ${isDisabled ? 'disabled' : ''}`
    li.innerHTML = `<a class="page-link ${className}" href="#" data-pc-target-table-id="${tableId}">${text}</a>`
    return li
  }

  #getStateFromEvent = (event) => {
    const trigger = event.target.closest('[data-pc-target-table-id]')
    return trigger ? this.#paginators[trigger.dataset.pcTargetTableId] : null
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

    state.$filteredRows = state.$allRows.filter(row => {
      if (state.searchQuery === '') {
        return true
      }
      if (state.searchColumn === 'all') {
        return row.textContent.toLowerCase().includes(state.searchQuery)
      } else {
        const cell = row.querySelector(`td[data-search-key="${state.searchColumn}"]`)
        return cell ? cell.textContent.toLowerCase().includes(state.searchQuery) : false
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
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'click', `.${PcTablePaginator.PAGE_LINK}`, this.#onPageClick)
    EventHandler.off(document.body, 'click', `.${PcTablePaginator.PREVIOUS_BUTTON}`, this.#onPrevClick)
    EventHandler.off(document.body, 'click', `.${PcTablePaginator.NEXT_BUTTON}`, this.#onNextClick)
  }
}
