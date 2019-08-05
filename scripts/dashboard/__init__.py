from scripts.dashboard.diversification_statistics import get_offerer_count, get_offerer_with_stock_count, \
    get_offerers_with_offer_available_on_discovery_count, get_offerers_with_non_cancelled_bookings_count, \
    get_offers_with_user_offerer_and_stock_count, get_offers_available_on_discovery_count, \
    get_offers_with_non_cancelled_bookings_count, get_all_bookings_count, get_all_used_bookings_count, \
    get_all_cancelled_bookings_count
from scripts.dashboard.finance_statistics import get_total_deposits, get_total_amount_spent, get_total_amount_to_pay, \
    get_top_20_offers_table, get_top_20_offerers_table_by_number_of_bookings, get_top_20_offerers_by_amount_table, \
    get_not_cancelled_bookings_by_departement
from scripts.dashboard.users_statistics import count_activated_users, count_users_having_booked, \
    get_mean_number_of_bookings_per_user_having_booked, get_mean_amount_spent_by_user, \
    get_non_cancelled_bookings_by_user_departement

__all__ = ('get_offerer_count',
           'get_offerer_with_stock_count',
           'get_offerers_with_offer_available_on_discovery_count',
           'get_offerers_with_non_cancelled_bookings_count',
           'get_offers_with_user_offerer_and_stock_count',
           'get_offers_available_on_discovery_count',
           'get_offers_with_non_cancelled_bookings_count',
           'get_all_bookings_count',
           'get_all_used_bookings_count',
           'get_all_cancelled_bookings_count',
           'get_total_deposits',
           'get_total_amount_spent',
           'get_total_amount_to_pay',
           'get_top_20_offers_table',
           'get_top_20_offerers_table_by_number_of_bookings',
           'get_top_20_offerers_by_amount_table',
           'get_not_cancelled_bookings_by_departement',
           'get_non_cancelled_bookings_by_user_departement',
           'count_activated_users',
           'count_users_having_booked',
           'get_mean_number_of_bookings_per_user_having_booked',
           'get_mean_amount_spent_by_user'
           )
