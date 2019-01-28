# Comprendre pourquoi un évènement n'est pas recommandé

```bash
pc python
user = User.query.filter_by(email='pctest.jeune.93@btmx.fr').first()
department_codes = ['75', '78', '91', '94', '93', '95']\
                        if user.departementCode == '93'\
                        else [user.departementCode]
get_occasions_by_type(Event, occasion_id=8, user=user, department_codes=department_codes)
get_occasions_by_type(Event, occasion_id=9, user=user, department_codes=department_codes)
get_occasions_by_type(Event, occasion_id=10, user=user, department_codes=department_codes)
```
