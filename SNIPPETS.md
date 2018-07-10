# Comprendre pourquoi un évènement n'est pas recommandé

```bash
pc python
```

```bash
app.datascience.get_occasions_by_type(app.model.Event, occasion_id=381)
```

```bash
user = client_user
```

```bash
departement_codes = ['75', '78', '91', '94', '93', '95']\
                        if user.departementCode == '93'\
                        else [user.departementCode]
```

```bash
app.datascience.get_occasions_by_type(app.model.Event, occasion_id=381, user=user, departement_codes=departement_codes)
```
