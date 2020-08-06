from typing import Optional

from domain.pro_offerers.paginated_offerers import PaginatedOfferers
from domain.pro_offerers.paginated_offerers_repository import PaginatedOfferersRepository
from models import Offerer, VenueSQLEntity, UserSQLEntity
from repository.offerer_queries import filter_offerers_with_keywords_string, query_filter_offerer_by_user


class PaginatedOfferersSQLRepository(PaginatedOfferersRepository):
    def with_status_and_keywords(self,
                                 user_id: int,
                                 user_is_admin: bool,
                                 page: Optional[int],
                                 pagination_limit: int,
                                 only_validated_offerers: bool,
                                 is_filtered_by_offerer_status: bool,
                                 keywords: Optional[str] = None) -> PaginatedOfferers:
        # TODO: to remove
        current_user = UserSQLEntity.query.get(user_id)

        query = Offerer.query

        if not user_is_admin:
            query = query_filter_offerer_by_user(query)

        if is_filtered_by_offerer_status:
            if only_validated_offerers:
                query = query.filter(Offerer.validationToken == None)
            else:
                query = query.filter(Offerer.validationToken != None)

        if keywords is not None:
            query = query.join(VenueSQLEntity)
            query = filter_offerers_with_keywords_string(query, keywords)
            total_data_count = query.distinct().count()
        else:
            total_data_count = query.count()
        query = query.order_by(Offerer.name)
        offerers = query.all()

        for offerer in offerers:
            offerer.append_user_has_access_attribute(current_user)

        query = query.paginate(page, per_page=int(pagination_limit), error_out=False)
        results = query.items
        total = total_data_count

        return PaginatedOfferers(results, total)
