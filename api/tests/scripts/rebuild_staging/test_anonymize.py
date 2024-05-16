import pathlib
import re

import sqlalchemy as sa

import pcapi


ANONYMIZE_SQL_PATH = pathlib.Path(pcapi.__path__[0]) / "scripts" / "rebuild_staging" / "anonymize.sql"


class AnonymizeTest:
    def test_run_sql_script(self, db_session):
        sql = []
        with ANONYMIZE_SQL_PATH.open() as fp:
            for line in fp.readlines():
                line = line.strip()
                # Look for lines like "\i .../rebuild_staging/dependency.sql`
                # that load external SQL files with functions. Fragile but
                # should work (or visibly fail).
                if match := re.match("\\\\i .*?/rebuild_staging/(.*)", line):
                    filename = match.group(1)
                    path = ANONYMIZE_SQL_PATH.parent / filename
                    sql.append(path.read_text())
                else:
                    sql.append(line)
        sql = "\n".join(sql)
        db_session.execute(sa.text(sql))
